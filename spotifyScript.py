import json
import re
import base64
from requests import post, get

class SpotifyAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self.get_token()
    
    def get_token(self):
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
        
        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        result = post(url, headers=headers, data=data)
        json_result = json.loads(result.content)
        return json_result["access_token"]
    
    def get_auth_header(self):
        return {"Authorization": "Bearer " + self.token}

    def search_for_artist(self, artist_name):
        url = "https://api.spotify.com/v1/search"
        headers = self.get_auth_header()
        query = f"?q={artist_name}&type=artist&limit=1"
        
        query_url = url + query   
        result = get(query_url, headers=headers)
        json_result = json.loads(result.content)["artists"]["items"]
        if len(json_result) == 0:
            print("Artist not found")
            return None
        return json_result[0]

    def get_songs_by_artist(self, artist_id):
        url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=CA"
        headers = self.get_auth_header()
        result = get(url, headers=headers)
        json_result = json.loads(result.content)["tracks"]

        artist_genres = self.get_artist_genres(artist_id)
        print(f"Artist Genres: {', '.join(artist_genres)}") 
        return json_result

    def get_track_details(self, track_id):
        url = f"https://api.spotify.com/v1/tracks/{track_id}"
        headers = self.get_auth_header()
        result = get(url, headers=headers)
        return json.loads(result.content)

    def get_playlist_id(self, playlist_link):
        pattern = r"playlist\/([a-zA-Z0-9]+)"
        match = re.search(pattern, playlist_link)
        return match.group(1) if match else None

    def get_playlist_details(self, playlist_id):
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        headers = self.get_auth_header()
        result = get(url, headers=headers)
        return json.loads(result.content)

    def get_artist_dictionary(self, playlist):
        artist_list = [track["track"]["artists"][0]["name"] for track in playlist["tracks"]["items"]]
        artist_list_no_duplicates = list(set(artist_list))
        
        artist_dictionary = {}
        for artist in artist_list_no_duplicates:
            count = artist_list.count(artist)
            artist_dictionary[artist] = count
        
        return artist_dictionary

    def get_artist_genres(self, artist_id):
        url = f"https://api.spotify.com/v1/artists/{artist_id}"
        headers = self.get_auth_header()
        result = get(url, headers=headers)
        return json.loads(result.content).get("genres", [])

    def print_dictionary(self, artist_dictionary):
        for artist, count in artist_dictionary.items():
            print(f"{artist}: {count}")
