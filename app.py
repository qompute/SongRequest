from config import spotify_client_id, spotify_client_secret
import json
import base64
import queue
import requests
from flask import Flask, render_template, request, Response, redirect, url_for

app = Flask(__name__)

song_queue = queue.Queue()

@app.route('/')
def host():
    return render_template('host.html')

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
            result = {'id': item['id'], 'name_artist': f'{item["name"]} - {", ".join(artists)}'}
            search_results.append(result)
        return render_template('request.html', search_query=query, search_results=search_results)
    return request_song()

@app.route('/song/<song_id>', methods=['POST'])
def song_requested(song_id):
    header = {'Authorization': f'Bearer {access_token}'}
    r = requests.get(f'https://api.spotify.com/v1/tracks/{song_id}', headers=header)
    if r.status_code == 200:
        song = {'id': r.json()['id'],
                'name': r.json()['name'],
                'artists': [a['name'] for a in r.json()['artists']]}
        song_queue.put(json.dumps(song))
        print(json.dumps(song))
    return redirect(url_for('request_song'))

@app.route('/stream')
def listen_for_requests():
    def stream():
        while True:
            next_song = song_queue.get()
            yield f'data: {next_song}\n\n'
    return Response(stream(), mimetype='text/event-stream')

def get_spotify_token():
    body = {'grant_type': 'client_credentials'}
    string_bytes = f'{spotify_client_id}:{spotify_client_secret}'.encode('ascii')
    encoded_bytes = base64.b64encode(string_bytes)
    encoded_string = encoded_bytes.decode('ascii')
    header = {'Authorization': f'Basic {encoded_string}'}
    r = requests.post('https://accounts.spotify.com/api/token', data=body, headers=header)
    return r.json()['access_token']

access_token = get_spotify_token()
