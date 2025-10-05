import os
import uuid
import threading
import subprocess
import glob
from flask import Flask, session, request, redirect, render_template, url_for, jsonify, send_from_directory
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from src.data import extract_track_info, get_audio_features, get_artist_genres
from src.analysis import (
    generate_statistics, analyze_genres, find_exact_duplicates, 
    find_different_versions, generate_taste_profile # Ditambahkan
)

app = Flask(__name__)
app.secret_key = os.urandom(24)
DOWNLOAD_FOLDER = os.path.join(app.root_path, 'static', 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope='user-library-read user-top-read',
    cache_handler=cache_handler,
    show_dialog=True
)

tasks = {}

def get_spotify_client():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return None
    return spotipy.Spotify(auth_manager=sp_oauth)

def run_analysis_task(task_id, analysis_type, playlist_url):
    try:
        tasks[task_id]['status'] = 'running'
        tasks[task_id]['progress'] = 10
        tasks[task_id]['message'] = 'Mengautentikasi & mengambil data...'
        token_info = tasks[task_id]['token_info']
        thread_auth_manager = SpotifyOAuth(client_id=os.getenv("SPOTIPY_CLIENT_ID"), client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"), redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"), scope='user-library-read user-top-read', show_dialog=True)
        if sp_oauth.is_token_expired(token_info):
            token_info = thread_auth_manager.refresh_access_token(token_info['refresh_token'])
        sp_thread_client = spotipy.Spotify(auth=token_info['access_token'], requests_timeout=20, retries=3)
        
        df = pd.DataFrame()
        # ... (Logika fetch data tetap sama) ...
        if analysis_type == 'liked_songs':
            results = sp_thread_client.current_user_saved_tracks(limit=50)
            tracks_raw = results['items']
            while results['next']:
                results = sp_thread_client.next(results)
                tracks_raw.extend(results['items'])
            df = extract_track_info(tracks_raw)
        elif analysis_type == 'playlist':
            import re
            match = re.search(r'playlist/([a-zA-Z0-9]+)', playlist_url)
            if match:
                playlist_id = match.group(1)
                results = sp_thread_client.playlist_tracks(playlist_id, limit=100)
                tracks_raw = results['items']
                while results['next']:
                    results = sp_thread_client.next(results)
                    tracks_raw.extend(results['items'])
                df = extract_track_info(tracks_raw)

        if df.empty: raise ValueError("Gagal mengambil data lagu.")
        
        tasks[task_id]['progress'] = 50
        tasks[task_id]['message'] = 'Menganalisis fitur audio...'
        df = get_audio_features(sp_thread_client, df)
        
        tasks[task_id]['progress'] = 75
        tasks[task_id]['message'] = 'Menghitung statistik...'
        artist_genre_map = get_artist_genres(sp_thread_client, df['artist_ids'].tolist())
        stats = generate_statistics(df)
        profile = generate_taste_profile(df) # <-- DITAMBAHKAN KEMBALI
        genres = analyze_genres(df, artist_genre_map)
        duplicates = find_exact_duplicates(df)
        versions = find_different_versions(df)

        tasks[task_id]['progress'] = 90
        tasks[task_id]['message'] = 'Menyelesaikan...'
        stats['top_artists'] = stats['top_artists'].to_dict()
        stats['top_years'] = stats['top_years'].to_dict()
        tasks[task_id]['result'] = {
            'type': 'analysis', 'data': { 'stats': stats, 'profile': profile, 'genres': genres, 'duplicates': duplicates.to_dict('records'), 'versions': versions.to_dict('records')}
        }
        tasks[task_id]['status'] = 'complete'

    except Exception as e:
        import traceback
        traceback.print_exc()
        tasks[task_id]['status'] = 'failed'; tasks[task_id]['message'] = str(e)

def run_download_task(task_id, spotify_url, format, quality):
    try:
        token_info = tasks[task_id]['token_info']
        sp_thread_client = spotipy.Spotify(auth=token_info['access_token'])
        
        tasks[task_id]['status'] = 'running'
        tasks[task_id]['progress'] = 5
        tasks[task_id]['message'] = 'Mengambil daftar lagu...'

        import re
        tracks_to_download = []
        if 'track' in spotify_url:
            track = sp_thread_client.track(spotify_url)
            tracks_to_download.append({'name': track['name'], 'url': track['external_urls']['spotify']})
        elif 'playlist' in spotify_url or 'album' in spotify_url:
            if 'playlist' in spotify_url:
                results = sp_thread_client.playlist_tracks(spotify_url)
            else: # Album
                results = sp_thread_client.album_tracks(spotify_url)
            
            for item in results['items']:
                track = item if 'playlist' in spotify_url else item
                if track and track.get('name'):
                    tracks_to_download.append({'name': track['name'], 'url': track['external_urls']['spotify']})
            while results['next']:
                results = sp_thread_client.next(results)
                for item in results['items']:
                    track = item if 'playlist' in spotify_url else item
                    if track and track.get('name'):
                        tracks_to_download.append({'name': track['name'], 'url': track['external_urls']['spotify']})
        
        if not tracks_to_download:
            raise ValueError("Tidak ada lagu yang ditemukan dari URL.")

        tasks[task_id]['result'] = {
            'type': 'download_queue',
            'tracks': [{'name': t['name'], 'status': 'Menunggu'} for t in tracks_to_download]
        }
        tasks[task_id]['message'] = f'Antrean siap: {len(tracks_to_download)} lagu.'
        tasks[task_id]['progress'] = 10

        for i, track in enumerate(tracks_to_download):
            tasks[task_id]['result']['tracks'][i]['status'] = 'Mengunduh...'
            tasks[task_id]['message'] = f'Mengunduh lagu {i+1}/{len(tracks_to_download)}: {track["name"]}'
            
            cmd = ["spotdl", track['url'], "--output", DOWNLOAD_FOLDER, "--format", format]
            if format in ["mp3", "m4a"] and quality != "best":
                cmd.extend(["--bitrate", quality])
            
            subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            tasks[task_id]['result']['tracks'][i]['status'] = 'Selesai'

        tasks[task_id]['status'] = 'complete'
        tasks[task_id]['message'] = 'Semua download selesai!'

    except Exception as e:
        import traceback
        traceback.print_exc()
        tasks[task_id]['status'] = 'failed'; tasks[task_id]['message'] = str(e)


# ... (Semua rute dari @app.route('/') hingga akhir tetap sama persis) ...
@app.route('/')
def index():
    sp = get_spotify_client()
    if not sp: return redirect(url_for('login'))
    user = None
    try: user = sp.current_user()
    except: session.clear(); sp = None
    return render_template('index.html', user_logged_in=bool(sp), user=user)
@app.route('/downloader')
def downloader():
    sp = get_spotify_client()
    if not sp: return redirect(url_for('login'))
    user = sp.current_user()
    return render_template('downloader.html', user=user)
@app.route('/login')
def login(): return redirect(sp_oauth.get_authorize_url())
@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))
@app.route('/callback')
def callback(): sp_oauth.get_access_token(request.args.get('code')); return redirect(url_for('index'))
@app.route('/start_analysis', methods=['POST'])
def start_analysis():
    sp = get_spotify_client()
    if not sp: return redirect(url_for('login'))
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'token_info': sp_oauth.get_cached_token()}
    thread = threading.Thread(target=run_analysis_task, args=(task_id, request.form.get('analysis_type'), request.form.get('playlist_url', '')))
    thread.start()
    return redirect(url_for('loading', task_id=task_id))
@app.route('/start_download', methods=['POST'])
def start_download():
    sp = get_spotify_client()
    if not sp: return redirect(url_for('login'))
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'token_info': sp_oauth.get_cached_token()}
    thread = threading.Thread(target=run_download_task, args=(task_id, request.form.get('spotify_url'), request.form.get('format'), request.form.get('quality')))
    thread.start()
    return redirect(url_for('loading', task_id=task_id))
@app.route('/loading/<task_id>')
def loading(task_id): return render_template('loading.html', task_id=task_id)
@app.route('/status/<task_id>')
def status(task_id): return jsonify(tasks.get(task_id, {}))
@app.route('/results/<task_id>')
def results(task_id):
    task = tasks.get(task_id, {})
    if task.get('status') != 'complete' or task.get('result', {}).get('type') != 'analysis':
        return "Tugas belum selesai atau bukan hasil analisis.", 404
    return render_template('results.html', **task.get('result', {}).get('data', {}))
@app.route('/download_file/<filename>')
def download_file(filename): return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)
if __name__ == '__main__': app.run(debug=True, port=8888)