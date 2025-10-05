# src/data.py
from .auth import get_spotify_client
import pandas as pd

def get_all_liked_tracks():
    sp = get_spotify_client()
    results = sp.current_user_saved_tracks()
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def extract_track_info(tracks):
    data = []
    for item in tracks:
        track = item['track']
        data.append({
            'name': track['name'],
            'artists': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'release_date': track['album']['release_date'],
            'duration_ms': track['duration_ms'],
            'spotify_id': track['id'],
            'external_url': track['external_urls']['spotify'],
            'added_at': item['added_at']
        })
    return data

def get_audio_features(df):
    sp = get_spotify_client()
    unique_ids = df['spotify_id'].unique().tolist()
    batch_size = 100
    all_features = []
    for i in range(0, len(unique_ids), batch_size):
        batch_ids = unique_ids[i:i + batch_size]
        try:
            features_batch = sp.audio_features(batch_ids)
            all_features.extend(features_batch)
        except Exception as e:
            print(f"Gagal mengambil audio features: {e}")
            print("Melanjutkan tanpa audio features...")
            return df

    all_features = [f for f in all_features if f is not None]
    feature_df = pd.DataFrame(all_features)
    feature_df.rename(columns={'id': 'spotify_id'}, inplace=True)
    merged_df = df.merge(feature_df, on='spotify_id', how='left')
    return merged_df