import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

def get_spotify_client():
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
            scope='user-library-read user-top-read user-library-modify'
        ),
        requests_timeout=20,    # Waktu tunggu dinaikkan menjadi 20 detik
        retries=3,              # Coba lagi hingga 3 kali jika gagal
        status_retries=3,       # Coba lagi juga untuk status error tertentu
        backoff_factor=0.5      # Jeda sesaat sebelum mencoba lagi
    )
    return sp