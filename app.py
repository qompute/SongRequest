from config import spotify_client_id, spotify_client_secret, redirect_uri
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

@app.route('/login')
def login_to_spotify():
    params = {'client_id': spotify_client_id,
              'response_type': 'code',
              'redirect_uri': redirect_uri,
              'scope': 'user-modify-playback-state',
              'show_dialog': 'true'}
    url = 'https://accounts.spotify.com/authorize?' + "&".join([f'{k}={v}' for k, v in params.items()])
    return redirect(url)

@app.route('/callback')
def callback():
    global access_token
    if 'code' not in request.args:
        return redirect(url_for('host'))
    body = {'grant_type': 'authorization_code',
            'code': request.args['code'],
            'redirect_uri': redirect_uri}
    string_bytes = f'{spotify_client_id}:{spotify_client_secret}'.encode('ascii')
    encoded_bytes = base64.b64encode(string_bytes)
    encoded_string = encoded_bytes.decode('ascii')
    header = {'Authorization': f'Basic {encoded_string}'}
    r = requests.post('https://accounts.spotify.com/api/token', data=body, headers=header)
    access_token = r.json()['access_token']
    return redirect(url_for('host'))

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
            images = item['album']['images']
            image_url = ''
            for image in images:
                if image['height'] == 64 and image['width'] == 64:
                    image_url = image['url']
            result = {
                'id': item['id'],
                'name': item["name"],
                'artists': ", ".join(artists),
                'image_url': image_url
            }
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
        params = {'uri': r.json()['uri']}
        r = requests.post('https://api.spotify.com/v1/me/player/queue', data=params, headers=header)
    return redirect(url_for('request_song'))

@app.route('/stream', methods=['GET'])
def listen_for_requests():
    def stream():
        while True:
            next_song = song_queue.get()
            yield f'event: Song request\ndata: {next_song}\n\n'
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
