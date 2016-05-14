from requests import get
from lxml import html
from datetime import datetime
from gmusicapi import Mobileclient
from json import dumps
from sys import exit

google_user = ''
google_password = ''
url = 'http://www1.wdr.de/radio/1live/on-air/1live-webradio/plan-b-channel-playlist-100.html'

request = get(url)
parsed_doc = html.fromstring(request.content)
parent_elements = parsed_doc.xpath('//body//*/div[@class="table"]/table/tbody/tr')

songs = []

for parent in parent_elements:
    children = [child for child in parent.iterchildren() if child.tag == 'td']

    if len(children) == 2:
        song = {}
        song['artist'] = children[0].text_content()
        song['title'] = children[1].text_content()
        songs.append(song)

# print dumps(songs, indent=4)

print 'Extracted {} songs from {}.'.format(len(songs), url)
print

# Login to Google Play Music and create new playlist from fetched songs
api = Mobileclient()
logged_in = api.login(google_user, google_password, Mobileclient.FROM_MAC_ADDRESS)
if not logged_in:
	exit('Could not log in to Google Play Music')

# Search songs in Google Play Music and obtain track IDs
storeIds = []
not_found_songs = []
for song in songs:
	print u'Searching for "{s[artist]} - {s[title]}"...'.format(s=song)

	search_term = u'{s[artist]} {s[title]}'.format(s=song)
	result = api.search(search_term)
	song_hits = result['song_hits']

	print 'Found {} song(s).'.format(len(song_hits))

	if len(song_hits) == 0:
		not_found_songs.append(song)
	else:
		song_hit = song_hits[0] # Only add first search result for this song to playlist
		track = song_hit['track']

		msg = u'Adding "{t[artist]} - {t[title]}"'.format(t=track)
		if 'album' in track.keys():
			msg = msg + u' from album "{t[album]}"'.format(t=track)
		if 'year' in track.keys():
			msg = msg + u' ({t[year]})'.format(t=track)
		print msg
		print

		storeIds.append(track['storeId'])

# Create Google Play Music playlist and insert songs
playlist_name = '1live {:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
playlist_id = api.create_playlist(playlist_name)
api.add_songs_to_playlist(playlist_id, storeIds)

print 'Added {} songs to playlist "{}".'.format(len(storeIds), playlist_name)
print '{} songs were extracted initially.'.format(len(songs), url)
print
print 'Songs not found in Google Play Music:'
for song in not_found_songs:
	print u'{s[artist]} - {s[title]}'.format(s=song)