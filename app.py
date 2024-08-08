import os
from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv
from spotifyScript import SpotifyAPI

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

spotify = SpotifyAPI(client_id, client_secret)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/submit', methods=['POST'])
def submit():
    selected_option = request.form['options']
    if selected_option == 'option1':
        return redirect(url_for('artist', option=selected_option))
    elif selected_option == 'option2':
        return redirect(url_for('playlist_input', option=selected_option))
    else:
        return f'You selected: {selected_option}'

@app.route('/artist', methods=['GET', 'POST'])
def artist():
    option = request.args.get('option')
    if request.method == 'POST':
        artist_name = request.form['artist']
        result = spotify.search_for_artist(artist_name)
        artist_id = result["id"]
        songs = spotify.get_songs_by_artist(artist_id)
        songList = [song['name'] for song in songs]
        return render_template('display_songs.html', artist=artist_name, songs=songList)
    return render_template('artist_form.html', option=option)

@app.route('/playlist_input', methods=['GET', 'POST'])
def playlist_input():
    option = request.args.get('option')
    if request.method == 'POST':
        playlist1 = request.form['playlist1']
        playlist2 = request.form['playlist2']
        return redirect(url_for('playlist_display', playlist1=playlist1, playlist2=playlist2))
    return render_template('playlist_input.html', option=option)

@app.route('/playlist_display', methods=['GET'])
def playlist_display():
    playlist1 = request.args.get('playlist1')
    playlist2 = request.args.get('playlist2')
    
    playlist1_id = spotify.get_playlist_id(playlist1)
    playlist1Details = spotify.get_playlist_details(playlist1_id)
    playlist1_track_count = playlist1Details["tracks"]["total"]
    
    playlist2_id = spotify.get_playlist_id(playlist2)
    playlist2Details = spotify.get_playlist_details(playlist2_id)
    playlist2_track_count = playlist2Details["tracks"]["total"]
    
    percent_diff = abs(playlist1_track_count - playlist2_track_count) / max(playlist1_track_count, playlist2_track_count) * 100
    in_range = percent_diff <= 25

    if not in_range:
        return redirect(url_for('playlist_input'))

    playlist1_dictionary = spotify.get_artist_dictionary(playlist1Details)
    playlist2_dictionary = spotify.get_artist_dictionary(playlist2Details)
    similar_artists = set(playlist1_dictionary.keys()).intersection(playlist2_dictionary.keys())
    
    total_similar_track = sum(playlist1_dictionary[artist] + playlist2_dictionary[artist] for artist in similar_artists)
    total_tracks = playlist1_track_count + playlist2_track_count
    similar_percentage = total_similar_track / total_tracks * 100
    
    return render_template('playlist_display.html', playlist_range=in_range, total_similar=total_similar_track, total=total_tracks, similar_percentage=int(similar_percentage))

if __name__ == "__main__":
    app.run(debug=True) #TODO: change to false once done editing
