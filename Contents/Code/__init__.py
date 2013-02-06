DFI_API_URL = "http://nationalfilmografien.service.dfi.dk/Movie.svc/json/%s"

rdict = {
	'&': '?',
	' ': '+',
	'æ': '%E6',
	'ø': '%F8',
	'å': '%E5',
	'(^en |^et |^de |^den |^der |^det )': ''
}

RE_REPLACE = Regex('|'.join(rdict.keys()), Regex.IGNORECASE)
RE_AGE = Regex('(\d)+')

####################################################################################################
def Start():

	HTTP.CacheTime = CACHE_1DAY

####################################################################################################
class DFIAgent(Agent.Movies):

	name = "DFI"
	languages = [Locale.Language.Danish]
	primary_provider = True

	def search(self, results, media, lang):

		url = DFI_API_URL % ('list?titlecontains=%s' % RE_REPLACE.sub(lambda m: rdict[m.group(0)], media.name.lower()))

		if media.year:
			url = '%s&startyear=%d&endyear=%d' % (url, int(media.year)-5, int(media.year)+5)
			Log.Debug(url)

		for DFI_Results in JSON.ObjectFromURL(url, sleep=2.0):
			DFI_Details = JSON.ObjectFromURL(DFI_API_URL % DFI_Results['ID'], cacheTime=CACHE_1MONTH, sleep=2.0)
			score = 100

			score = score - abs(String.LevenshteinDistance(media.name.lower(), DFI_Results['Name'].lower()))

			if media.year and int(media.year) > 1900:
				score = score - (abs(int(media.year) - int(DFI_Details.get('ReleaseYear'))) * 5)

			name = DFI_Results['Name']
			year = int(DFI_Details.get('ReleaseYear'))
			Log.Debug("after revising! [name]: %s, [year]: %s, [score]: %s, [resultname]: %s" % (media.name, media.year, score, DFI_Results['Name']))

			results.Append(MetadataSearchResult(
				id = str(DFI_Results['ID']),
				name = name,
				year = year,
				score = score,
				lang = 'da'
			))

	def update(self, metadata, media, lang):

		DFI_Metadata = JSON.ObjectFromURL(DFI_API_URL % metadata.id, cacheTime=CACHE_1MONTH, sleep=2.0)

		if 'Title' in DFI_Metadata: metadata.title = DFI_Metadata['Title']
		if 'OriginalTitle' in DFI_Metadata: metadata.original_title = DFI_Metadata['OriginalTitle'].strip()

		if 'Description' in DFI_Metadata and DFI_Metadata['Description'] is not None:
			metadata.summary = String.StripTags(DFI_Metadata['Description'])
		else:
			metadata.summary = None

		metadata.countries.clear()
		if 'ProductionCountries' in DFI_Metadata:
			## Get at list of all contries to translate from country code to readable text
			countrylist = JSON.ObjectFromURL('https://raw.github.com/umpirsky/country-list/master/country/cldr/en/country.json', cacheTime=CACHE_1MONTH)

			for country in DFI_Metadata['ProductionCountries']:
				if country in countrylist:
					metadata.countries.add(countrylist[country])

		if 'LengthInMin' in DFI_Metadata: metadata.duration = int(DFI_Metadata['LengthInMin']) * 60000
		if 'ReleaseYear' in DFI_Metadata: metadata.year = int(DFI_Metadata['ReleaseYear'])
		if 'SubCategories' in DFI_Metadata: metadata.genres = DFI_Metadata['SubCategories']
		if 'Keywords' in DFI_Metadata: metadata.tags = DFI_Metadata['Keywords']

		if 'Comment' in DFI_Metadata and DFI_Metadata['Comment'] is not None:
			metadata.trivia = String.StripTags(DFI_Metadata['Comment'])

		if 'Premiere' in DFI_Metadata:
			if 'PremiereDate' in DFI_Metadata['Premiere']:
				metadata.originally_available_at = Datetime.FromTimestamp(int(DFI_Metadata['Premiere']['PremiereDate'].rsplit('(')[1].rsplit('+',1)[0])/1000)

		metadata.directors.clear()
		metadata.writers.clear()
		metadata.producers.clear()
		metadata.roles.clear()

		for credit in DFI_Metadata['Credits']:
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

		if 'ProductionCompanies' in DFI_Metadata and len(DFI_Metadata['ProductionCompanies']) > 0:
			metadata.studio = DFI_Metadata['ProductionCompanies'][0]['Name']

		if 'Censorship' in DFI_Metadata:
			try:
				if RE_AGE.search(DFI_Metadata['Censorship']):
					metadata.content_rating_age = RE_AGE.search(DFI_Metadata['Censorship'].group(1))
					metadata.content_rating = DFI_Metadata['Censorship']
			except Exception, ex:
				Log.Debug("Exception obtaining content rating from DFI.")
				Log.Debug(ex)

		if 'Images' in DFI_Metadata and DFI_Metadata['Images'] is not None:
			DFI_Images = JSON.ObjectFromURL(DFI_Metadata['Images'], sleep=2.0)

			for image in DFI_Images:
				if image.get('Filetype').lower() in ('jpg', 'png'):
					if 'SrcMini' in image and image['ImageType'] == 'poster':
						try:
							poster = HTTP.Request(image['SrcMini'], timeout=120, sleep=2.0).content
							metadata.posters[image['SrcMini']] = Proxy.Preview(poster)
						except Exception, ex:
							Log.Debug('Poster problem')
							Log.Debug(ex)

					if 'SrcMini' in image and image['ImageType'] == 'photo':
						try:
							art = HTTP.Request(image['SrcMini'], timeout=120, sleep=2.0).content
							metadata.art[image['SrcMini']] = Proxy.Preview(art)
						except Exception, ex:
							Log.Debug('Art problem')
							Log.Debug(ex)
