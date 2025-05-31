from flask_cors import CORS
from flask import Flask, request, jsonify, session, redirect
import random
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_CLIENT_URL, SCOPE_MASTER
import utilities

'''
To run frontend:
cmd -> cd frontend
npm run dev

npm run --prefix frontend dev

To run backend:
python ./backend/main.py

mergesort!!
quicksort 
quick instersort?
'''

def remerge_history(History):
    for song_id in History:
        for sub_id in History[song_id]:
            if sub_id in History:
                History[song_id].extend(History[sub_id])
                History[song_id] = list(set(History[song_id]))

                
def mergePlaylist(songs, l, m, r, History):
    songs_copy = songs.copy()
    n1 = m - l + 1
    n2 = r - m
    L = [0] * (n1)  # create temp arrays
    R = [0] * (n2)
 
    for i in range(0, n1):  # Copy data to temp arrays L[] and R[]
        L[i] = songs_copy[l + i]
    for j in range(0, n2):
        R[j] = songs_copy[m + 1 + j]
    
    #for a in L:
    #    print('L:', a)
    #for a in R:
    #    print('R:', a)
    # Merge the temp arrays back into arr[l..r]
    i = 0     # Initial index of first subarray
    j = 0     # Initial index of second subarray
    k = l     # Initial index of merged subarray

    i = -1
    j = 0
    # Additional check if top element of L is less than first element of R to speed up sorting already sorted playlist 
    selectLeft = False
    selectRight = False
    if not (L[i]['id'] in History or R[j]['id'] in History):
        return False, L[i], R[j], songs
    
    if L[i]['id'] in History:
        if R[j]['id'] in History[L[i]['id']]:
            selectLeft = True
    if R[j]['id'] in History:
        if L[i]['id'] in History[R[j]['id']]:
            selectRight = True
    if not (selectLeft or selectRight):
        return False, L[i], R[j], songs
    if selectLeft and selectRight:
        print(f"Ambigous case: {L[i]['name']} - {R[j]['name']}\t\t{L[i]['id']} - {R[j]['id']}")
        return False, L[i], R[j], songs
    if selectRight:
        left_ids = [left_song['id'] for left_song in L]
        if R[j]['id'] in History:
            for idn in left_ids:
                if idn not in History[R[j]['id']]:
                    History[R[j]['id']].append(idn)
        else:
            History[R[j]['id']] = left_ids
    else:
        if L[i]['id'] in History:
            if R[j]['id'] not in History[L[i]['id']]:
                History[L[i]['id']].append(R[j]['id'])
        else:
            History[L[i]['id']] = [R[j]['id']]

    i = 0     # Initial index of first subarray
    j = 0     # Initial index of second subarray
    k = l     # Initial index of merged subarray
    while i < n1 and j < n2:
        selectLeft = False
        selectRight = False
        temphistory = []
        #if L[i] <= R[j]:
        #print(L[i]['name'], R[j]['name'])
        if not (L[i]['id'] in History or R[j]['id'] in History):
            return False, L[i], R[j], songs
        
        if L[i]['id'] in History:
            if R[j]['id'] in History[L[i]['id']]:
                selectLeft = True
        if R[j]['id'] in History:
            if L[i]['id'] in History[R[j]['id']]:
                selectRight = True
        
        if not (selectLeft or selectRight):
            return False, L[i], R[j], songs
        if selectLeft and selectRight:
            print(f"Ambigous case: {L[i]['name']} - {R[j]['name']}\t\t{L[i]['id']} - {R[j]['id']}")
            return False, L[i], R[j], songs



        if selectRight:
            songs_copy[k] = L[i]
            temphistory.append(L[i]['id'])
            i += 1
        else:
            songs_copy[k] = R[j]
            temphistory.append(R[j]['id'])
            j += 1

        k += 1
    
    while i < n1:  # Copy the remaining elements of L[], if there
        songs_copy[k] = L[i]
        if L[i]['id'] in History:
            for idn in temphistory:
                if idn not in History[L[i]['id']]:
                    History[L[i]['id']].append(idn)
        else:
            History[L[i]['id']] = temphistory
        temphistory.append(L[i]['id'])
        i += 1
        k += 1
 
    while j < n2:   # Copy the remaining elements of R[]
        songs_copy[k] = R[j]
        if R[j]['id'] in History:
            for idn in temphistory:
                if idn not in History[R[j]['id']]:
                    History[R[j]['id']].append(idn)
        else:
            History[R[j]['id']] = temphistory
        temphistory.append(R[j]['id'])
        j += 1
        k += 1

    return True, None, None, songs_copy
 

def mergeSortPlaylist(songs, l, r, History):
    if l < r:
        m = l+(r-l)//2  # Same as (l+r)//2, but avoids overflow for  large l and h
        finished, songLeft, songRight, songs = mergeSortPlaylist(songs, l, m, History)
        if not finished:
            return finished, songLeft, songRight, songs
        finished, songLeft, songRight, songs = mergeSortPlaylist(songs, m+1, r, History)
        if not finished:
            return finished, songLeft, songRight, songs
        finished, songLeft, songRight, songs_copy = mergePlaylist(songs, l, m, r, History)
        return finished, songLeft, songRight, songs_copy
    return True, None, None, songs


if __name__ == '__main__':
    app = Flask(__name__)
    app.config['CORS_HEADERS'] = "Content-Type"
    app.config['PROPAGATE_EXCEPTIONS'] = True
    cors = CORS(app)
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                        client_secret=SPOTIPY_CLIENT_SECRET,
                                                        redirect_uri=SPOTIPY_CLIENT_URL,
                                                        scope=SCOPE_MASTER))
    
    Database = {'songs': [], 'song_left': {}, 'song_right': {}, 'SelectHistory': {}, "playlist_id": None, "playlist_name": None}
    history_filename = 'history.txt'

    #utilities.dump_old_top_by_artist(spotify)
    #utilities.generate_must_have(spotify)
    #utilities.compare_new_old(spotify)


    @app.route("/sorter/select/<song_id>")
    def merge_sort_playlist_step(song_id):
        songs = Database['songs']
        songLeft = Database['song_left']
        songRight = Database['song_right'] 
        SelectHistory = Database['SelectHistory']

        # Select song
        if not (song_id == songLeft['id'] or song_id == songRight['id']):
            print('Something is wrong')
        if song_id == songLeft['id']:
            if song_id not in SelectHistory:
                SelectHistory[song_id] = [songRight['id']]
            else:
                if songRight['id'] not in SelectHistory[song_id]:
                    SelectHistory[song_id].append(songRight['id'])
        if song_id == songRight['id']:
            if song_id not in SelectHistory:
                SelectHistory[song_id] = [songLeft['id']]
            else:
                if songLeft['id'] not in SelectHistory[song_id]:
                    SelectHistory[song_id].append(songLeft['id'])
        # Sanity check?
        remerge_history(SelectHistory)
        
        finished, songLeft, songRight, songs_copy = mergeSortPlaylist(songs, 0, len(songs) - 1, SelectHistory)
        #finished, songLeft, song_right, songs_copy = mergeSortPlaylist(songs, 211, 240, SelectHistory)  
        if songLeft is None or songRight is None:
            songLeft = songs[-2]
            songRight = songs[-1]
        Database['songs'] = songs_copy
        Database['song_left'] = songLeft
        Database['song_right'] = songRight
        Database['SelectHistory'] = SelectHistory
        estimated = 100 * utilities.total_len_history(SelectHistory) / ((1 + len(songs)) * len(songs) / 2)
        save_history_to_file()

        if finished:
            songs_copy.reverse()
            utilities.reorder_playlist(spotify, Database['playlist_id'], songs_copy)
            return jsonify({'message': 'PLAYLIST IS SORTED NOW! YOU MAY CLOSE THIS PAGE!', 'finished':True, 'songs': songs_copy, 'song_left': songLeft, 'song_right': songRight, 'estimated_progress': estimated, 'success': True}) 
        
        return jsonify({'message': 'Success', 'finished':False, 'songs': songs_copy, 'song_left': songLeft, 'song_right': songRight, 'estimated_progress': estimated, 'success': True})     
    

    @app.route("/sorter/remove/<song_id>")
    def remove_songs_from_playlist(song_id):
        spotify.playlist_remove_all_occurrences_of_items(Database['playlist_id'], [song_id])
        remove_song_from_history(song_id)
        nr = -1

        for i, song in enumerate(Database['songs']):
            if song['id'] == song_id:
                nr = song['nr']
                Database['songs'].pop(i)
                break
        if nr >= 0:
            for song in Database['songs']:
                if song['nr'] > nr:
                    song['nr'] = song['nr'] - 1

        if song_id == Database['song_left']['id']:
            return merge_sort_playlist_step(Database['song_right']['id'])
        elif song_id == Database['song_right']['id']:
            return merge_sort_playlist_step(Database['song_left']['id'])
        else:
            print("SOMETHING'S WRONG")
            return jsonify({'message': "Success", 'success': False}) 
    
        return jsonify({'message': "Cannot remove. Local song?", 'success': False, 'songs': Database['songs']}) 
        

    @app.route("/sorter/remove_from_selection_history/<song_id>")
    def remove_song_from_history(song_id):
        SelectHistory = Database['SelectHistory']
        for song_history in SelectHistory:
            if song_id in SelectHistory[song_history]:
                SelectHistory[song_history].remove(song_id)

        if song_id in SelectHistory:
            SelectHistory.pop(song_id)
        #Database['SelectHistory'] = SelectHistory
        save_history_to_file()
        return jsonify({'message': "Removed"}) 

    @app.route("/history/clear")
    def clear_history():
        Database['SelectHistory'] = {}
        save_history_to_file()
        return jsonify({'message': "History cleared successfully."})
    

    @app.route("/get_songs/<playlist_id>/<reversed>/<start>/<stop>/")
    def get_songs_for_sorter(playlist_id, reversed, start, stop):
        reversed = int(reversed)
        start = int(start)
        stop = int(stop)
        songs, local_songs, playlist_len, playlist_name = utilities.get_songs_from_playlist(spotify, playlist_id)
        if len(songs) < 2:
            print('Playlist too short to sort. Crash imminent!')
        if stop < 1:
            start = 0
            stop = len(songs) - 1
        if reversed:
            songs.reverse()

        _, songLeft, songRight, songs_copy = mergeSortPlaylist(songs, start, stop, Database['SelectHistory'])
        #finished, songLeft, songRight, songs_copy = mergeSortPlaylist(songs, 211, 240, SelectHistory)  
        if songLeft is None or songRight is None:
            songLeft = songs[0]
            songRight = songs[1]
        Database['songs'] = songs_copy
        Database['song_left'] = songLeft
        Database['song_right'] = songRight
        Database['playlist_id'] = playlist_id
        Database['playlist_name'] = playlist_name
        read_history_file()
        return jsonify({'message': "Worked", 'local_songs': local_songs, 'songs':songs, 'song_left': Database['song_left'], 'song_right': Database['song_right'], 'playlist_len': playlist_len, 'playlist_name': playlist_name})

    
    @app.route("/get_playlists")
    def get_playlists_home():
        return jsonify({'message': "Ok.", 'playlists':utilities.get_playlists(spotify)})
    
    
    @app.route("/sorter/reverse/<playlist_id>")
    def reverse_playlist_route(playlist_id):
        utilities.reverse_playlist(spotify, playlist_id)
        return jsonify({'message': "Success"}) 


    @app.route("/sorter/shuffle/<playlist_id>")
    def shuffle_playlist(playlist_id):
        songs = Database['songs'].copy()
        random.shuffle(songs)
        utilities.reorder_playlist(spotify, playlist_id, songs)
        return jsonify({'message': "Success"}) 
    

    @app.route("/sorter/reorder")
    def reorder_route():
        utilities.reorder_playlist(spotify, Database['playlist_id'], Database['songs'])
        return jsonify({'message': "Reordered successfully."})
    

    @app.route("/playback/<song_id>/<offset>")
    def playback_start(song_id, offset):
        """
        id - spotify track id
        offset - playback start position in ms
        TODO:
        check if offset < track lenght      otherwise it will play next song i think?
        """



        uri = "spotify:track:" + song_id
        playlist_uri = "spotify:playlist:" + Database['playlist_id']

        #uri_2 = uri
        #print(Database['song_left'], Database['song_right'])
        if song_id == Database['song_left']['id']:
            uri_2 = "spotify:track:" + Database['song_right']['id']
        if song_id == Database['song_right'] ['id']:
            uri_2 = "spotify:track:" + Database['song_left']['id']
        uris = [uri, uri_2]
        #print(song_id)
        #print(uri, uri_2)
        #print(Database['song_left']['name'], Database['song_right']['name'])
        #print(uris)
        try:
            spotify.start_playback(context_uri=playlist_uri, offset={'uri': uri}, position_ms=offset)
            return jsonify({'success': True, 'message': "Working"})
        except:
            return jsonify({'success': False, 'message': "Cannot play a song. Check if you have Spotify opened and start any song."})
    

    @app.route("/playback/stop")
    def playback_pause():
        try:
            spotify.pause_playback()
            return jsonify({'message': "Playback paused."})
        except:
            return jsonify({'message': "Playback was already paused."})

    
    @app.route("/history/save")
    def save_history_to_file():
        SelectHistory = Database['SelectHistory']
        with open(history_filename, "w", encoding='utf-8') as f:
            f.write('')
            for song_id in SelectHistory:
                f.write(f'{song_id}')
                for sub in SelectHistory[song_id]:
                    f.write(f'\t{sub}')
                f.write('\n')
        return jsonify({'message': "History saved successfully."})


    @app.route("/history/read")
    def read_history_file():
        SelectHistory = {}
        if not os.path.isfile(history_filename):
            Database['SelectHistory'] = SelectHistory
            return jsonify({'message': "No history."})
        
        with open(history_filename, "r", encoding='utf-8') as f:
            for line in f:
                if line == '\n':
                    continue
                if line[0] == '#':
                    continue

                line = line.split()
                SelectHistory[line[0]] = line[1:]
        Database['SelectHistory'] = SelectHistory
        return jsonify({'message': "History read successfully."})
    

    app.run(debug=True)

