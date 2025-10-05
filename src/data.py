from .auth import get_spotify_client
import pandas as pd
from .database import is_cache_valid, get_tracks_from_db, save_tracks_to_db
from .config import get_config_value
from spotipy.exceptions import SpotifyException

def extract_track_info(tracks_raw):
    data = []
    for item in tracks_raw:
        if not item or not (track := item.get('track')) or not track.get('id'):
            continue
        
        artists = track.get('artists', [])
        data.append({
            'name': track.get('name', 'N/A'),
            'artists': ', '.join([a['name'] for a in artists]),
            'artists_list': [a['name'] for a in artists],
            'artist_ids': [a['id'] for a in artists],
            'album': track.get('album', {}).get('name', 'N/A'),
            'release_date': track.get('album', {}).get('release_date', 'N/A'),
            'duration_ms': track.get('duration_ms', 0),
            'spotify_id': track.get('id'),
            'external_url': track.get('external_urls', {}).get('spotify', ''),
            'added_at': item.get('added_at', '')
        })
    return pd.DataFrame(data)

def _fetch_from_spotify_and_save(source_id, fetch_function, *args, **kwargs):
    print(f"Mengambil data dari Spotify API untuk: {source_id}")
    
    results = fetch_function(*args, **kwargs)
    tracks_raw = results['items']
    while results['next']:
        results = get_spotify_client().next(results)
        tracks_raw.extend(results['items'])

    df = extract_track_info(tracks_raw)
    
    if not df.empty:
        sp = get_spotify_client()
        df_with_features = get_audio_features(sp, df.copy())
        save_tracks_to_db(source_id, df_with_features)
        return df_with_features
    return pd.DataFrame()

def get_all_liked_tracks():
    source_id = 'liked_songs'
    expiration = get_config_value('Cache', 'expiration_hours')
    if is_cache_valid(source_id, expiration):
        print("Memuat 'Liked Songs' dari cache database...")
        return get_tracks_from_db(source_id)
    
    sp = get_spotify_client()
    return _fetch_from_spotify_and_save(source_id, sp.current_user_saved_tracks, limit=50)

def get_tracks_from_playlist(playlist_id):
    source_id = f"playlist_{playlist_id}"
    expiration = get_config_value('Cache', 'expiration_hours')
    if is_cache_valid(source_id, expiration):
        print(f"Memuat playlist {playlist_id} dari cache database...")
        return get_tracks_from_db(source_id)
        
    sp = get_spotify_client()
    return _fetch_from_spotify_and_save(source_id, sp.playlist_tracks, playlist_id=playlist_id, limit=100)

# --- PERUBAHAN DI SINI ---
def get_audio_features(sp_client, df):
    ids = df['spotify_id'].dropna().unique().tolist()
    if not ids: return df

    features_list = []
    for i in range(0, len(ids), 100):
        batch = ids[i:i+100]
        try:
            batch_features = sp_client.audio_features(batch)
            features_list.extend(f for f in batch_features if f)
        except Exception as e:
            print(f"Peringatan: Gagal mengambil audio features. Error: {e}")
    
    if not features_list:
        print("Peringatan: Tidak ada data audio features yang berhasil diambil.")
        return df

    features_df = pd.DataFrame(features_list).rename(columns={'id': 'spotify_id'})
    return df.merge(features_df, on='spotify_id', how='left')

# --- PERUBAHAN DI SINI ---
def get_artist_genres(sp_client, artist_ids):
    unique_ids = list(set(aid for sublist in artist_ids for aid in sublist))
    if not unique_ids: return {}
    
    genre_map = {}
    for i in range(0, len(unique_ids), 50):
        batch = unique_ids[i:i+50]
        try:
            for artist in sp_client.artists(batch)['artists']:
                if artist: genre_map[artist['id']] = artist['genres']
        except Exception:
            pass
    return genre_map