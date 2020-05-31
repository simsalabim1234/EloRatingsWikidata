import os
import requests
import zipfile
import collections
import json
import calendar
import pywikibot
import time
import random
from datetime import datetime
from pywikibot import pagegenerators
import xml.etree.ElementTree as ET

def check_published_ratings(year, month):
    # Filter for available Elo ratings
    currentYear = datetime.now().year
    
    published = 0
    if (year < 2009) :
        if (month == 1):
            published = 1
        elif (month == 4):
            published = 1
        elif (month == 7):
            published = 1
        elif (month == 10):
            published = 1
        else:
            pass
    elif (year == 2009) :
        if (month == 1):
            published = 1
        elif (month == 4):
            published = 1
        elif (month == 7):
            published = 1
        elif (month == 9):
            published = 1
        elif (month == 11):
            published = 1
        else:
            pass
    elif ( (year == 2010) or (year == 2011) ) :
        if (month == 1):
            published = 1
        elif (month == 3):
            published = 1
        elif (month == 5):
            published = 1
        elif (month == 7):
            published = 1
        elif (month == 9):
            published = 1
        elif (month == 11):
            published = 1
        else:
            pass
    elif (year == 2012) :
        if (month == 2):
            pass
        elif (month == 4):
            pass
        elif (month == 6):
            pass          
        else:
            published = 1
    elif (year == currentYear) :
        if (month <= now.month):
            published = 1
        else:
            pass
    else :
        published = 1        

    return published

def get_FIDE_Elo_ratings(year, month):
    month_word = calendar.month_name[month]

    month_abb = (month_word[0:3]).lower()
    year_abb = str(year)[2:4]

    # last month without standard_ : August 2012
    if (year < 2012) :
        filename = month_abb + year_abb + 'frl'
    elif (year == 2012):
        if ( month < 9) :
            filename = month_abb + year_abb + 'frl'
        else:
            filename = "standard_" + month_abb + year_abb + 'frl'
    else:
        filename = "standard_" + month_abb + year_abb + 'frl'
    
    #XML format
    if (year > 2012) :
        filename = "standard_" + month_abb + year_abb + 'frl_xml'
        
    url = 'http://ratings.fide.com/download/' + filename + '.zip'

    myfile = requests.get(url)
    open(filename + '.zip', 'wb').write(myfile.content)

    # Unzip File
    zip_ref = zipfile.ZipFile(filename + '.zip')
    textfilename = zip_ref.namelist()[0]
    zip_ref.extractall()
    zip_ref.close()
    
    return textfilename

def fetch_missing_ratings(year, month): 
# Query players with missing Elo rating for the considered month

    wikidata_site = pywikibot.Site('wikidata', 'wikidata')
    repo = wikidata_site.data_repository()

    dataset_query = """SELECT ?item WHERE
    {{
      ?item wdt:P106 wd:Q10873124.
      ?item wdt:P1440 ?fide .
      MINUS {{
          ?item p:P1087 [pq:P585 ?date ] .
          FILTER ( MONTH(?date)={0} && YEAR(?date)={1} ) .
      }}
    }} LIMIT 100""".format(year, month)

    QIDs = []
    for itemkey in pagegenerators.WikidataSPARQLPageGenerator(dataset_query, site=wikidata_site):
        QIDs.append(itemkey.title())

    fideIDs = []
    for i, item in enumerate(QIDs):
        Qitem = pywikibot.ItemPage(repo, item)
        Qitem.get()
        fideIDs.append(Qitem.claims['P1440'][0].getTarget())
        
    return QIDs, fideIDs

def match_IDs_old(year, month, textfilename, QIDs, fideIDs):
    "Read rating from FIDE rating list"
    elo = []
    
    # open text-file
    f = open(textfilename,"r", encoding="Latin-1")
    
    # Get Elo rating
    if (year < 2013) :
        content = f.readlines()
        for lineNo in range(len(content)): 
            if (lineNo == 0):
                continue
            else :
                line = content[lineNo]
                if (year == 2001) :
                    if (month == 1):
                        elo = line[59:63]
                    else :
                        elo = line[60:64]
                elif (year == 2002) :
                    if (month == 1):
                        elo = line[59:63]
                    elif (month == 10):
                        elo = line[53:57]
                    else :
                        elo = line[60:64]
                elif (year == 2012) :
                    if (month < 9) :
                        elo = line[53:57] 
                    else :
                        elo = line[109:113]      
                else :
                    elo = line[53:57]
        
        # Get FIDE ID
        fideid = line.split(' ')[0]
        if (fideid == '') :
            fideid = line.split(' ')[1]
            if (fideid == '') :
                fideid = line.split(' ')[2]
                if (fideid == '') :
                    fideid = line.split(' ')[3]
                    if (fideid == '') :
                        fideid = line.split(' ')[4]
                        if (fideid == '') :
                            fideid = line.split(' ')[5]
    
    # close and delete text file
    f.close()
    os.remove(textfilename)

    FideID_QId = collections.defaultdict()
    
    FideID_Elo = collections.defaultdict()
    
    QId_Elo = collections.defaultdict()
    
    for idx, qid in QIDs :
        FideID = fideIDs[idx] 
        FideID_QId[int(FideID)] = qid
    
    
    
    
    
    for k in FideID_QId:
        try:
            QId = FideID_QId[k]
            Elo = FideID_Elo[k]
            QId_Elo[QId] = {"Elo": Elo, "FideID" : str(k)}
        except KeyError:
            continue

    return QId_Elo

def match_IDs(year, month, textfilename, QIDs, fideIDs):
    # Get Elo rating
    # Last month without xml-file: Juli 2012
        
    if (year < 2013) :
        if (month < 8) :
            return match_IDs_textfile(year, month, textfilename, QIDs, fideIDs)
        else :
            return match_IDs_XMLfile(year, month, textfilename, QIDs, fideIDs)
    else :
        return match_IDs_XMLfile(year, month, textfilename, QIDs, fideIDs)
       
def match_IDs_textfile(year, month, textfilename, QIDs, fideIDs):
    elo = []

    f = open(textfilename,"r", encoding="Latin-1")

    content = f.readlines()
    for lineNo in range(len(content)): 
        if (lineNo == 0):
            continue
        else :
            line = content[lineNo]
            if (year == 2001) :
                if (month == 1):
                    elo = line[59:63]
                else :
                    elo = line[60:64]
            elif (year == 2002) :
                if (month == 1):
                    elo = line[59:63]
                elif (month == 10):
                    elo = line[53:57]
                else :
                    elo = line[60:64]
            elif (year == 2012) :
                if (month < 9) :
                    elo = line[53:57] 
                else :
                    elo = line[109:113]      
            else :
                elo = line[53:57]
        
        # Get FIDE ID
        fideid = line.split(' ')[0]
        if (fideid == '') :
            fideid = line.split(' ')[1]
            if (fideid == '') :
                fideid = line.split(' ')[2]
                if (fideid == '') :
                    fideid = line.split(' ')[3]
                    if (fideid == '') :
                        fideid = line.split(' ')[4]
                        if (fideid == '') :
                            fideid = line.split(' ')[5]
    
    f.close()
    os.remove(textfilename)

    FideID_QId = collections.defaultdict()
    
    FideID_Elo = collections.defaultdict()
    
    QId_Elo = collections.defaultdict()
    
    return QId_Elo

def match_IDs_XMLfile(year, month, textfilename, QIDs, fideIDs):
    tree = ET.parse(textfilename)
    root = tree.getroot()
    
    QId_Elo = collections.defaultdict()
    FideID_Elo = collections.defaultdict()
     
    for player in root.findall('player'):
        FideID = player.find('fideid').text
        Elo = player.find('rating').text
        FideID_Elo[int(FideID)] = Elo
        
    for idx, qid in QIDs :
        try:
            FideID = fideIDs[idx] 
            Elo = FideID_Elo[int(FideID)]
            QId_Elo[qid] = {"Elo": Elo, "FideID" : str(FideID)}
        except KeyError:
            continue
        
    return QId_Elo

def Wikidata_import_ratings(QId_Elo, year, month):
    currentDay = datetime.now().day
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    
    wikidata_site = pywikibot.Site('wikidata', 'wikidata')
    repo = wikidata_site.data_repository()
    with open('elo_ratings_for_import.json') as fh:
        i = 0
        fh.write("[ \n")
        for QId, EloEntry in QId_Elo.items():
            if ( i > 0 ) :
                fh.write(', \n')
            i = i+1
            fh.write("    ")
            line = {"QID": QId, "P1087": int(EloEntry["Elo"]), "P585":{ "Y":int(year) , "M":month }, "P248":"Q27038151", "P1440": EloEntry["FideID"], "P813":{ "Y":currentYear, "M":currentMonth, "D":currentDay }}
            json.dump(line, fh, ensure_ascii=False)
        fh.write("\n")
        fh.write("]")
        fh.close()

    with open('elo_ratings_for_import.json') as fh:
        inputdata = json.load(fh)

    for i, obj in enumerate(inputdata):
        random.shuffle(inputdata)
        eloAlreadySet = False
    
        Qitem = pywikibot.ItemPage(repo, obj['QID'])
        while True:
            try:
                Qitem = pywikibot.ItemPage(repo, obj['QID'])
                Qitem.get()
                break
            except pywikibot.exceptions.MaxlagTimeoutError as e:
                print(e)
                time.sleep(10)    

        if Qitem.claims and 'P1087' in Qitem.claims:
            for eloClaim in Qitem.claims['P1087']:
                if eloClaim.qualifiers and 'P585' in eloClaim.qualifiers:
                    for j, dummy in enumerate(eloClaim.qualifiers['P585']):
                        pointInTime = eloClaim.qualifiers['P585'][j].getTarget()
                        if pointInTime.year==obj['P585']['Y'] and pointInTime.month==obj['P585']['M']:
                            eloAlreadySet = True
                            print('{}: Elo claim for {}-{:02d} already exists with value {}; skip'.format(obj['QID'], obj['P585']['Y'], obj['P585']['M'], eloClaim.getTarget().amount))

        if eloAlreadySet==False:
            newElo = pywikibot.Claim(repo, 'P1087')
            newElo.setTarget(value=pywikibot.WbQuantity(site=repo, amount=obj['P1087']))
            Qitem.addClaim(newElo)

            timestmp = pywikibot.Claim(repo, 'P585')
            timestmp.setTarget(value=pywikibot.WbTime(year=obj['P585']['Y'], month=obj['P585']['M']))
            newElo.addQualifier(timestmp)

            if 'P1440' in obj:
                statedIn = pywikibot.Claim(repo, 'P248')
                statedIn.setTarget(value=pywikibot.ItemPage(repo, 'Q27038151')); # Q27038151 is ratings.fide.org
                fideId = pywikibot.Claim(repo, 'P1440')
                fideId.setTarget(value=obj['P1440'])
                retrieved = pywikibot.Claim(repo, 'P813')
                retrieved.setTarget(value=pywikibot.WbTime(year=obj['P813']['Y'], month=obj['P813']['M'], day=obj['P813']['D']))
                newElo.addSources([statedIn, fideId, retrieved])
            elif 'P854' in obj:
                url = pywikibot.Claim(repo, 'P854')
                url.setTarget(value=obj['P854'])
                retrieved = pywikibot.Claim(repo, 'P813')
                retrieved.setTarget(value=pywikibot.WbTime(year=obj['P813']['Y'], month=obj['P813']['M'], day=obj['P813']['D']))
                if 'P1476' in obj:
                    title = pywikibot.Claim(repo, 'P1476')
                    title.setTarget(value=pywikibot.WbMonolingualText(text=obj['P1476'], language='en'))
                    newElo.addSources([url, retrieved, title])
                else:
                    newElo.addSources([url, retrieved])

            print('{}: Elo claim for {}-{:02d} with value {} successfully added'.format(obj['QID'], obj['P585']['Y'], obj['P585']['M'], obj['P1087']))
        else:
            time.sleep(1) # wait 1 second to avoid reading too fast from the API

    print('All done, task finished')        