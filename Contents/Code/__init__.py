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
	accept_from = "com.plexapp.agents.imdb"

	def search(self, results, media, lang):
		#DFI_Search = JSON.ObjectFromURL(DFI_SEARCH_URL % str(media.name).replace(' ','+').replace('æ','%E6').replace('ø','%F8').replace('å','%E5').replace('Æ','%C6').replace('Ø','%D8').replace('Å','%C5').lower() )
		url = DFI_RESULT_URL % ('list?titlecontains=' + re.sub('&','?', re.sub(' ','+', re.sub('æ','%E6', re.sub('ø','%F8', re.sub('å','%E5', re.sub('^en |^et |^de |^den |^der |^det ','' ,str(media.name).lower())))))))
		if media.year:
			url += '&startyear=' + str(int(media.year)-5) + '&endyear=' + str(int(media.year)+5)
			Log.Debug(url)
		DFI_Search = JSON.ObjectFromURL(url)
		for DFI_Results in DFI_Search:
			DFI_Details = JSON.ObjectFromURL(DFI_RESULT_URL % DFI_Results['ID'])
			id = str(DFI_Results['ID'])
			if str(DFI_Results['Name']).lower() == str(media.name).lower():
				score = 100
			else:
				score = 100 - String.LevenshteinDistance( str(media.name).lower(), str(DFI_Results['Name']).lower())
			if media.year:
				score = score - (abs(int(media.year)-int(DFI_Details.get('ReleaseYear',str(media.year))))*5)
			name = DFI_Results['Name']
			year = int(DFI_Details.get('ReleaseYear'))
			Log.Debug("after revising! [name]: %s, [year]: %s, [score]: %s, [resultname]: %s" %(media.name, media.year, score, DFI_Results['Name']) )
			results.Append(MetadataSearchResult(id = id, score = score, name = name , lang = lang, year = year))
			
			
	def update(self, metadata, media, lang): 
	   
	   # Only use data from DFI if the user has set the language for this section to Danish (Dansk)
	   if lang == 'da':
		   
		   proxy = Proxy.Preview
		   DFI_metadata = JSON.ObjectFromURL(DFI_RESULT_URL % metadata.id)
			
		   if 'Title' in DFI_metadata: metadata.title = DFI_metadata['Title']
		   if 'Description' in DFI_metadata: metadata.summary = DFI_metadata['Description']
		   if 'OriginalTitle' in DFI_metadata :metadata.original_title = DFI_metadata['OriginalTitle']

		   if 'ProductionCountries' in DFI_metadata :
		   		## Get at list of all contries to translate from country code to readable text
				countrylist = JSON.ObjectFromURL('https://raw.github.com/umpirsky/country-list/master/country/cldr/en/country.json')
				## Clear the metadata, in case old language codes has been added (from pre release)
				metadata.countries.clear() 
			   	for country in DFI_metadata['ProductionCountries']:
		   			metadata.countries.add(countrylist[country])
			   			
				
		   if 'LengthInMin' in DFI_metadata : metadata.duration =  int(DFI_metadata['LengthInMin']) * 60000
		   if 'ReleaseYear' in DFI_metadata : metadata.year = int(DFI_metadata['ReleaseYear'])
		   if 'Category' in DFI_metadata : metadata.collections.add(DFI_metadata['Category'])
		   if 'SubCategories' in DFI_metadata : metadata.genres = DFI_metadata['SubCategories']
		   if 'Keywords' in DFI_metadata : metadata.tags = DFI_metadata['Keywords']
		   if 'Comment' in DFI_metadata : metadata.trivia = DFI_metadata['Comment']
		   if 'Premiere' in DFI_metadata:
			   if 'PremiereDate' in DFI_metadata['Premiere']:
					metadata.originally_available_at = date.fromtimestamp(int(DFI_metadata['Premiere']['PremiereDate'].rsplit('(')[1].rsplit('+',1)[0])/1000)
				
		   metadata.directors.clear()
		   metadata.writers.clear()
		   metadata.producers.clear()
		   metadata.roles.clear()

		   for credit in DFI_metadata['Credits']:
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
			   except Exception, ex:
				   Log.Debug("Exception obtaining content rating from DFI.")
				   Log.Debug(ex)
		   

		   if 'Images' in DFI_metadata and DFI_metadata.get('Images') is not None:
		   	   try:
				   DFI_images = JSON.ObjectFromURL(DFI_metadata['Images'])   
				   for image in DFI_images:
				   	   if image.get('Filetype').lower() == 'jpg' or image.get('Filetype').lower() == 'png':
			   
						   if 'SrcMini' in image and image['ImageType'] == 'poster':
							   poster = HTTP.Request(image['SrcMini'], timeout = 120)
							   metadata.posters[image['SrcMini']] = proxy(poster, sort_order = 1)
						   if 'SrcMini' in image and image['ImageType'] == 'photo':
							   art = HTTP.Request(image['SrcMini'], timeout = 120)
							   metadata.art[image['SrcMini']] = proxy(art, sort_order = 1)
			   except Exception, ex:
			   		Log.Debug('Image problem')
			   		Log.Debug(ex)
			
				
		
				
				
			
			
			
			
			
		
		
			