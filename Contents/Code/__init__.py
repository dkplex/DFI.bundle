from datetime import date
import re
DFI_SEARCH_URL = "http://nationalfilmografien.service.dfi.dk/Movie.svc/json/list?titlecontains=%s"
DFI_RESULT_URL = "http://nationalfilmografien.service.dfi.dk/Movie.svc/json/%s"

def Start():
  HTTP.CacheTime = CACHE_1HOUR * 4
  
class DFIAgent(Agent.Movies):
    name = "DFI"
    languages = [Locale.Language.Danish]
    primary_provider = True

    def search(self, results, media, lang):
        DFI_Search = JSON.ObjectFromURL(DFI_SEARCH_URL % (String.Quote(media.name)))
        for DFI_Results in DFI_Search:
            results.Append(MetadataSearchResult(id = str(DFI_Results['ID']), score = 100, name = DFI_Results['Name'], lang = lang))    
            
    def update(self, metadata, media, lang): 
       
       # Only use data from Moviepilot if the user has set the language for this section to Danish (Dansk)
       if lang == 'da':
           
           proxy = Proxy.Preview
           DFI_metadata = JSON.ObjectFromURL(DFI_RESULT_URL % metadata.id)
            
           if 'Title' in DFI_metadata: metadata.title = DFI_metadata['Title']
           if 'Description' in DFI_metadata: metadata.summary = DFI_metadata['Description']
           if 'OriginalTitle' in DFI_metadata :metadata.original_title = DFI_metadata['OriginalTitle']

           if 'ProductionCountries' in DFI_metadata : 
               for country in DFI_metadata['ProductionCountries']:
                   metadata.countries.add(country)
                
           if 'LengthInMin' in DFI_metadata : metadata.duration =  int(DFI_metadata['LengthInMin']) * 60000
           if 'ReleaseYear' in DFI_metadata : metadata.year = int(DFI_metadata['ReleaseYear'])
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
               Log.Info(credit['Type'])
               if credit['Type'] == 'Direction':
                   metadata.directors.add(credit['Name'])
               if credit['Type'] == 'Screenwriter' or credit['Type'] == 'Script':
                   metadata.writers.add(credit['Name'])
               if credit['Type'] == 'Producer':
                   producer.append(credit['Name'])
               if credit['Type'] == 'Voice' or credit['Type'] == 'Actors':
                   role = metadata.roles.new()
                   role.role = credit['Description']
                   role.actor = credit['Name']
           
           if 'ProductionCompanies' in DFI_metadata: metadata.studio = DFI_metadata['ProductionCompanies'][0]['Name']
           if 'Censorship' in DFI_metadata:
               try:
                   if re.search('(\d)+', DFI_metadata['Censorship']):
                       metadata.content_rating_age = re.match('(\d)+', DFI_metadata['Censorship'])
                       metadata.content_rating = DFI_metadata['Censorship']
               except:
                   Log("Exception obtaining content rating from DFI.")

           if 'Images' in DFI_metadata:
               DFI_images = JSON.ObjectFromURL(DFI_metadata['Images'])   
               for image in DFI_images:
                   if 'SrcMini' in image and image['ImageType'] == 'poster':
                       poster = HTTP.Request(image['SrcMini'])
                       metadata.posters[image['SrcMini']] = proxy(poster, sort_order = 1)
                   if 'SrcMini' in image and image['ImageType'] == 'photo':
                       art = HTTP.Request(image['SrcMini'])
                       metadata.art[image['SrcMini']] = proxy(art, sort_order = 1)
            
            
                
        
                
                
            
            
            
            
            
        
        
            