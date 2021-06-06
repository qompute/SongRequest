# SongRequest

SongRequest is a web application that connects to your Spotify queue and allows others to add songs to your queue. It is great for handling song requests when playing music in a group setting!

## How to run locally
This project uses [Flask](https://flask.palletsprojects.com). To install flask, run
```
pip install Flask
```
To create your own local instance, you will need a [Spotify Developer](https://developer.spotify.com) account to use the Spotify API.

1. Log in to your Spotify account, go to your [Dashboard](https://developer.spotify.com/dashboard), and create a new app. You should see a Client ID and Client Secret on the project page.

2. Create a new file in the project directory named `config.py`. This file will contain the API keys:
```
spotify_client_id = "your_spotify_client_id"
spotify_client_secret = "your_spotify_client_secret"
redirect_uri = "http://localhost:5000/callback"
```
Replace `your_spotify_client_id` with your Client ID and replace `your_spotify_client_secret` with your Client Secret.

3. Export the flask app. In your project directory, run:
```
export FLASK_APP=app
```

4. To run the server, run:
```
flask run --host=0.0.0.0
```
Setting `--host=0.0.0.0` allows your server to be publicly available on the network.

5. Visit [localhost:5000](http://localhost:5000) in a web browser to view the web page!

You need a Spotify Premium account to add songs to your queue. Once you have logged in to the homepage, then you can visit [localhost:5000/request](http://localhost:5000/request) to search and request a song. To request a song from another device, you will need to access the IP address of the host device. For example, if the IP of the device you are running from is `192.168.1.100`, then you would need to access `192.168.1.100:5000/request` on another device to request a song.
