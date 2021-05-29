from config import spotify_client_id, spotify_client_secret
import base64
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/request')
def request_song():
    return render_template('request.html', search_query="", search_results=[])

@app.route('/search', methods=['GET'])
def search_song():
    if 'q' not in request.args:
        return request_song()
    query = request.args['q']
    if len(query) == 0:
        return request_song()
    params = {'q': query, 'type': 'track'}
    header = {'Authorization': f'Bearer {access_token}'}
    r = requests.get('https://api.spotify.com/v1/search', params=params, headers=header)
    if 'tracks' in r.json() and 'items' in r.json()['tracks']:
        search_results = []
        for item in r.json()['tracks']['items']:
            artists = [a['name'] for a in item['artists']]
            search_results.append(f'{item["name"]} - {", ".join(artists)}')
        return render_template('request.html', search_query=query, search_results=search_results)
    return request_song()

def get_spotify_token():
    body = {'grant_type': 'client_credentials'}
    string_bytes = f'{spotify_client_id}:{spotify_client_secret}'.encode('ascii')
    encoded_bytes = base64.b64encode(string_bytes)
    encoded_string = encoded_bytes.decode('ascii')
    header = {'Authorization': f'Basic {encoded_string}'}
    r = requests.post('https://accounts.spotify.com/api/token', data=body, headers=header)
    return r.json()['access_token']

access_token = get_spotify_token()
