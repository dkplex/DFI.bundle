from datetime import date
import re
DFI_SEARCH_URL = "http://nationalfilmografien.service.dfi.dk/Movie.svc/json/list?%s"
DFI_RESULT_URL = "http://nationalfilmografien.service.dfi.dk/Movie.svc/json/%s"

def Start():
  HTTP.CacheTime = CACHE_1HOUR * 4
  
class DFIAgent(Agent.Movies):
    name = "DFI"
    languages = [Locale.Language.Danish]
    primary_provider = True
    
    def search(self, results, media, lang):
        DFI_Search = JSON.ObjectFromURL(DFI_SEARCH_URL % media.name)
        for DFI_Results in DFI_Search:
            results.Append(MetadataSearchResult(id = DFI_Results['ID'], score = 100, name = DFI_Results['Name'] ))    
            
    def update(self, metadata, media, lang): 
        DFI_metadata = JSON.ObjectFromURL(DFI_RESULT_URL % metadata.id)
        if 'Title' in DFI_metadata: metadata.title = DFI_metadata['Title']
        if 'Description' in DFI_metadata: metadata.summary = DFI_metadata['Description']
        if 'OriginalTitle' in DFI_metadata :metadata.original_title = DFI_metadata['OriginalTitle']
        #if 'ProductionCountries' in DFI_metadata : metadata.countries = DFI_metadata['ProductionCountries']
        if 'ProductionCountries' in DFI_metadata : 
            for country in DFI_metadata['ProductionCountries']:
                metadata.countries.add(country)
                
        if 'LengthInMin' in DFI_metadata : metadata.duration =  int(DFI_metadata['LengthInMin']) * 60000
        if 'ReleaseYear' in DFI_metadata : metadata.year = DFI_metadata['ReleaseYear']
        if 'SubCategories' in DFI_metadata : metadata.genres = DFI_metadata['SubCategories']
        if 'Comment' in DFI_metadata : metadata.trivia = DFI_metadata['Comment']
        if 'Premiere' in DFI_metadata:
            if 'PremiereDate' in DFI_metadata['Premiere']:
                metadata.originally_available_at = date.fromtimestamp(int(DFI_metadata['Premiere']['PremiereDate'].rsplit('(')[1].rsplit('+',1)[0])/1000)
                
        metadata.directors.clear()
        metadata.writers.clear()
        metadata.producers.clear()
        metadata.roles.clear()
        
        for credit in DFI_metadata['Credits']:
            if credit['Type'] is 'Director':
                metadata.directors.add(credit['Name'])
            if credit['Type'] is 'Screenwriter':
                metadata.writers.add(credit['Name'])
            if credit['Type'] is 'Producer':
                producer.append(credit['Name'])
            if credit['Type'] is 'Voice' or credit['Type'] is 'Actor':
                role = metadata.roles.new()
                role.role = credit['Description']
                role.actor = credit['Name']
        if 'ProductionCompanies' in DFI_metadata: metadata.studio = DFI_metadata['ProductionCompanies'][0]['name']
        if 'Censorship' in DFI_metadata:
            try:
                if re.search('(\d)+', DFI_metadata['Censorship']):
                    metadata.content_rating_age = re.match('(\d)+', DFI_metadata['Censorship'])
                metadata.content_rating = DFI_metadata['Censorship']
            except:
                Log("Exception obtaining content rating from DFI.")
                
            
            
                
        
                
                
            
            
            
            
            
        
        
            