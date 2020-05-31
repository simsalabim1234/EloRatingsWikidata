import pywikibot
import time
from pywikibot import pagegenerators

wikidata_site = pywikibot.Site('wikidata', 'wikidata')
repo = wikidata_site.data_repository()

inputdata = []
dataset_query = """SELECT DISTINCT ?item WHERE {
  ?item p:P1087 [ pq:P585 ?date; wikibase:rank ?rank ]; wdt:P570 ?dod .
  FILTER(?rank != wikibase:DeprecatedRank) .
  FILTER(?date >= ?dod) .
}"""

for itemkey in pagegenerators.WikidataSPARQLPageGenerator(dataset_query, site=wikidata_site):
    print('Input Output Putt kaputt')
    inputdata.append(itemkey.title())

for i, item in enumerate(inputdata):
    Qitem = pywikibot.ItemPage(repo, item)
    Qitem.get()
    
    print()
    print('=== Item {} ({}/{}) ==='.format(item, i+1, len(inputdata)))
    if not Qitem.claims:
        print('* No claims found; skip item')
        continue
    
    if 'P570' not in Qitem.claims:
        print('* No date of death found; skip item')
        continue
        
    if len(Qitem.claims['P570'])>1:
        print('* More than one date of death found; skip item')
        continue
        
    dod = Qitem.claims['P570'][0].getTarget()
    if dod.precision < 9:
        print('* Date of death precision less than "year"; skip item')
        continue
    
    if 'P1087' not in Qitem.claims:
        print('* No Elo numbers found; skip item')
        continue
        
    for claim in Qitem.claims['P1087']:
        if not claim.qualifiers or 'P585' not in claim.qualifiers:
            print('* Found claim (value {}) without P585 qualifier; skip claim'.format(claim.getTarget().amount))
            continue
        
        if claim.qualifiers['P585'][0].getTarget().precision < 10:
            print('* Elo point in time precision less than "month"; skip claim')
            continue
        
        if claim.getRank() == 'deprecated':
            #print('* Claim is already deprecated; skip claim')
            continue
            
        if dod.year < claim.qualifiers['P585'][0].getTarget().year or (dod.precision>=10 and dod.year == claim.qualifiers['P585'][0].getTarget().year and dod.month < claim.qualifiers['P585'][0].getTarget().month):
            claim.changeRank('deprecated', summary='deprecate [[Property:P1087]] claim for point of time after subject’s date of death')
            print('* Set {} --> P1087 --> "{}" --> P585 --> "{:04d}-{:02d}" to "deprecated rank" (dod: {:04d}-{:02d}-{:02d}, precision {})'.format(item, claim.getTarget().amount, claim.qualifiers['P585'][0].getTarget().year, claim.qualifiers['P585'][0].getTarget().month, dod.year, dod.month, dod.day, dod.precision))

print()
print('All done, task finished')