import subfunctions
       
year_list = list(range(2014, 2021))
month_list = list(range(1,13))

for year in year_list :
    print('Year: ' + str(year))
    for month in month_list :
        
        published = subfunctions.check_published_ratings(year, month)

        if (published == 1) :
            print('Month: ' + str(month))
            filename = subfunctions.get_FIDE_Elo_ratings(year, month)
    
            QIDs, fideIDs = subfunctions.fetch_missing_ratings(year, month)
    
            QIDs_ratings = subfunctions.match_IDs(year, month, filename, QIDs, fideIDs)
    
            subfunctions.Wikidata_import_ratings(QIDs_ratings, year, month)

        print('All done for this year and month!')
        
print('Finished completely!')