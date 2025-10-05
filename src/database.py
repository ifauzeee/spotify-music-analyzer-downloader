import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DB_FILE = "spotify_data.db"

def get_db_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            id TEXT PRIMARY KEY, name TEXT, album TEXT, release_date TEXT, duration_ms INTEGER,
            external_url TEXT, danceability REAL, energy REAL, valence REAL, acousticness REAL,
            instrumentalness REAL, liveness REAL, speechiness REAL
        )""")
        cursor.execute("CREATE TABLE IF NOT EXISTS artists (id TEXT PRIMARY KEY, name TEXT)")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS track_artists (
            track_id TEXT, artist_id TEXT, PRIMARY KEY (track_id, artist_id),
            FOREIGN KEY (track_id) REFERENCES tracks (id), FOREIGN KEY (artist_id) REFERENCES artists (id)
        )""")
        cursor.execute("CREATE TABLE IF NOT EXISTS cache_log (source_id TEXT PRIMARY KEY, last_fetched TIMESTAMP)")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS source_tracks (
            source_id TEXT, track_id TEXT, added_at TEXT, PRIMARY KEY (source_id, track_id),
            FOREIGN KEY (track_id) REFERENCES tracks (id)
        )""")
        conn.commit()

def is_cache_valid(source_id, expiration_hours):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT last_fetched FROM cache_log WHERE source_id = ?", (source_id,))
        result = cursor.fetchone()
        if result:
            last_fetched = datetime.fromisoformat(result[0])
            if datetime.now() - last_fetched < timedelta(hours=expiration_hours):
                return True
    return False

def get_tracks_from_db(source_id):
    query = """
    SELECT
        t.*,
        GROUP_CONCAT(a.name, '|||') AS artists_list_str,
        GROUP_CONCAT(a.id, '|||') AS artist_ids_list_str,
        st.added_at
    FROM tracks t
    JOIN track_artists ta ON t.id = ta.track_id
    JOIN artists a ON ta.artist_id = a.id
    JOIN source_tracks st ON t.id = st.track_id
    WHERE st.source_id = ?
    GROUP BY t.id, st.added_at
    """
    with get_db_connection() as conn:
        df = pd.read_sql_query(query, conn, params=(source_id,))
    
    if not df.empty:
        df['artists_list'] = df['artists_list_str'].str.split('|||')
        df['artist_ids'] = df['artist_ids_list_str'].str.split('|||')
        df['artists'] = df['artists_list'].apply(', '.join)
        df.drop(columns=['artists_list_str', 'artist_ids_list_str'], inplace=True)
        df.rename(columns={'id': 'spotify_id'}, inplace=True)
    return df

def save_tracks_to_db(source_id, df):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            # PERBAIKAN DI SINI: Mapping dari 'spotify_id' ke 'id'
            track_data = {
                'id': row.get('spotify_id'),
                'name': row.get('name'),
                'album': row.get('album'),
                'release_date': row.get('release_date'),
                'duration_ms': row.get('duration_ms'),
                'external_url': row.get('external_url'),
                'danceability': row.get('danceability'),
                'energy': row.get('energy'),
                'valence': row.get('valence'),
                'acousticness': row.get('acousticness'),
                'instrumentalness': row.get('instrumentalness'),
                'liveness': row.get('liveness'),
                'speechiness': row.get('speechiness')
            }
            
            columns = ', '.join(track_data.keys())
            placeholders = ', '.join(['?'] * len(track_data))
            cursor.execute(f"INSERT OR REPLACE INTO tracks ({columns}) VALUES ({placeholders})", list(track_data.values()))
            
            if 'artist_ids' in row and 'artists_list' in row and isinstance(row['artist_ids'], list):
                for artist_id, artist_name in zip(row['artist_ids'], row['artists_list']):
                    cursor.execute("INSERT OR IGNORE INTO artists (id, name) VALUES (?, ?)", (artist_id, artist_name))
                    cursor.execute("INSERT OR IGNORE INTO track_artists (track_id, artist_id) VALUES (?, ?)", (row['spotify_id'], artist_id))
            
            cursor.execute("INSERT OR REPLACE INTO source_tracks (source_id, track_id, added_at) VALUES (?, ?, ?)", (source_id, row['spotify_id'], row['added_at']))

        cursor.execute("INSERT OR REPLACE INTO cache_log (source_id, last_fetched) VALUES (?, ?)", (source_id, datetime.now().isoformat()))
        conn.commit()

init_db()