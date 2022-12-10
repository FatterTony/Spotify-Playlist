
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm
import time
import music_tag
import os
from difflib import SequenceMatcher
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth


###Variables to set:
SPOTIPY_CLIENT_ID = 'e610f95bd7d5443fa34bfd5c26550fdb'
SPOTIPY_CLIENT_SECRET = '27d8c89d2ce645deab07bec8a540f944'
# assign directory
directory = 'E:\\Private\\Handy\\Music\\' #Directory of music
save_at = 'C:\\Users\\Philipp\\Desktop\\not_found.txt' #Directory and Filename where all tracks that could not be found in Spotify are saved.
save_at2 = 'C:\\Users\\Philipp\\Desktop\\not_added.txt' #Directory and Filename where all tracks that are nod added because of strong missmatch between search and found are saved.

#Add playlist information
username = 'phlppphlpp'
playlist_id = '3nvdPWyfXuTlvnTo2t169B'

#Add token for spotify api access. Get new token here: https://developer.spotify.com/console/get-track/
scope = 'playlist-modify-private'
token = 'BQCVPeediPRWLXLh8BpVdAO9qLhP5t-LdURFVw9-ZhwTIi1CGNu2rDzbD-YZSLtuFwX0WU56XGs0RY4gs15mptRJ-ePftAO2X_Iv4rG9NtIaGqL2bkcBogg61KuITPXmGdIunmBPIgM1JovTBsOlI_cPKYTvaziPJfo7Ka85M92ANLSSPip-tNS-7q0ocG8DcQ4W-CooXtMfyNs'



###Main program
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET ))
sp = spotipy.Spotify(auth=token)

not_found = []
not_added = []
for filename in tqdm(os.listdir(directory), colour="green", position=0, leave=True, bar_format='{l_bar}{bar}'):
    dir = os.path.join(directory, filename)

    # checking if it is a file
    if os.path.isfile(dir):

        #Extract track and album name from file
        f = music_tag.load_file(dir)
        track = str(f['title'])
        artist = str(f['artist'])

        #Test if extraction worked, otherwise skip this iteration and save as "not found"
        if not artist and not track:
            msg = '\x1b[0;30;41m' + " No Artist and Track extracted for: " + filename + '\x1b[0m'
            time.sleep(0.1)
            tqdm.write(msg)
            #print('\x1b[0;30;41m' + "No Artist and Track extracted for: " + filename + '\x1b[0m')
            #print("No Artist and Track extracted for: ", colored(filename, 'red'), " continued...")
            not_found.append(filename)
            #time.sleep(0.1)
            continue

        #Replace apostrophs and the & symbol
        track = track.replace("'", "")
        track = track.replace("&", "and")
        artist = artist.replace("'", "")
        artist = artist.replace("&", "and")



        #print(artist, track, sep = " - ")
        track_id = spotify.search(q=str(artist + " " + track), type='track')



        #track_id = spotify.search(q=str(track) + str(artist), type='track')
        if not track_id['tracks']['items']:
            msg = '\x1b[0;30;43m' + " No track ID found for: " + artist + " - " + track + '\x1b[0m'
            tqdm.write(msg)
            time.sleep(0.1)
            # print('\x1b[0;30;43m' + "No track ID found for: " + artist + " - " + track + '\x1b[0m')
            #print(colored("No track ID found for: " 'red'), end="\t")
            #print(artist, track, sep=" - ")
            not_found.append(artist + " - " + track)

        else:
            trackId = track_id['tracks']['items'][0]['id']
            artist_name = spotify.track(trackId)['album']['artists'][0]['name']
            song_name = spotify.track(trackId)['name']
            song_name = song_name.replace("'", "")
            song_name = song_name.replace("&", "and")
            artist_name = artist_name.replace("'", "")
            artist_name = artist_name.replace("&", "and")

            # Get again the artist and song titel of according track ID

            # Compare the strings
            sim_track = SequenceMatcher(None, track.lower(), song_name.lower())
            sim_artist = SequenceMatcher(None, artist.lower(), artist_name.lower())
            track_val = sim_track.ratio()
            artist_val = sim_artist.ratio()

            #if track_val < 0.9 or artist_val < 0.9:
                #print(artist + "    ", artist_name)
                #print(track + "   ", song_name)
            # Decide if you want to use it.
            if track_val < 0.65 and artist_val < 0.95 or artist_val < 0.7 or track_val < 0.45:
                msg = '\x1b[0;30;43m' + " Potential missmatch:" +'\x1b[0m'+ " searched <<" + artist + " - " + track + ">> found: <<" + artist_name + " - " + song_name + ">> similarity: [" + str(sim_artist.ratio()) + " " + str(sim_track.ratio()) + "]"
                tqdm.write(msg)
                not_added.append(artist + " - " + track + " ##### " + artist_name + " - " + song_name)
                time.sleep(0.1)
            else:
                msg = " " + artist + " - " + track
                tqdm.write(msg)
                sp.user_playlist_add_tracks(username, playlist_id, tracks=[trackId])





print('\x1b[6;30;42m' + "All tracks added..." + '\x1b[0m')




#Save not found tracks to .txt file
if os.path.exists(save_at):
    os.remove(save_at)


with open(save_at, 'w',encoding="utf-8") as fp:
    for item in not_found:
        fp.write("%s\n" % item)

#Save not not added tracks to .txt file
if os.path.exists(save_at2):
    os.remove(save_at2)

with open(save_at2, 'w',encoding="utf-8") as fp:
    for item in not_added:
        fp.write("%s\n" % item)



print("Not found tracks saved at: ", save_at)
print("Not added tracks (missmatch to large) saved at: ", save_at2)




