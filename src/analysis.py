# src/analysis.py
import pandas as pd
from fuzzywuzzy import fuzz
from collections import defaultdict
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def clean_title(title):
    common_words = [
        'feat', 'featuring', 'ft', 'prod', 'prod.', 'producer', 'remix', 'remastered',
        'live', 'acoustic', 'version', 'edit', 'original', 'radio', 'mix', 'extended',
        'official', 'music', 'video', 'studio', 'deluxe', 'anniversary', 'edition'
    ]
    title_lower = title.lower()
    for word in common_words:
        title_lower = title_lower.replace(f' {word} ', ' ').replace(f'({word})', ' ').replace(f'[{word}]', ' ')
    cleaned = re.sub(r'[^a-z0-9\s]', ' ', title_lower)
    cleaned = ' '.join(cleaned.split())
    return cleaned

def find_exact_duplicates(df):
    return df[df.duplicated(subset=['name', 'artists'], keep=False)]

def find_similar_titles_enhanced(df, threshold=85):
    similar_pairs = []
    titles = df['name'].tolist()
    processed_titles = [clean_title(t) for t in titles]
    df['cleaned_name'] = processed_titles

    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            ratio = fuzz.token_sort_ratio(df.iloc[i]['cleaned_name'], df.iloc[j]['cleaned_name'])
            if ratio < threshold:
                ratio = fuzz.token_set_ratio(df.iloc[i]['cleaned_name'], df.iloc[j]['cleaned_name'])
            if ratio >= threshold:
                similar_pairs.append({
                    'Track 1': df.iloc[i]['name'],
                    'Artist 1': df.iloc[i]['artists'],
                    'Track 2': df.iloc[j]['name'],
                    'Artist 2': df.iloc[j]['artists'],
                    'Match (%)': ratio
                })
    return pd.DataFrame(similar_pairs)

def group_similar_tracks(df, threshold=85, min_cluster_size=2):
    """
    Mengelompokkan lagu-lagu yang mirip ke dalam cluster menggunakan TF-IDF dan Agglomerative Clustering.
    Hanya menampilkan cluster dengan jumlah lagu >= min_cluster_size.
    """
    titles = df['cleaned_name'].tolist()
    if len(titles) < 2:
        print("Jumlah lagu tidak cukup untuk pengelompokan.")
        return {}

    # Gunakan TfidfVectorizer untuk mengubah teks menjadi vektor
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(titles)

    # Hitung cosine similarity dari matriks TF-IDF
    similarity_matrix = cosine_similarity(tfidf_matrix)

    # Konversi similarity ke distance (0 -> 1, 1 -> 0)
    distance_matrix = 1 - similarity_matrix

    # Gunakan Agglomerative Clustering
    clustering_model = AgglomerativeClustering(
        n_clusters=None,
        linkage='average',
        distance_threshold=1 - (threshold / 100.0), # threshold 85% -> distance 0.15
        metric='precomputed'
    )
    cluster_labels = clustering_model.fit_predict(distance_matrix)

    # Kelompokkan lagu berdasarkan label cluster
    clusters = defaultdict(list)
    for idx, label in enumerate(cluster_labels):
        clusters[label].append(df.iloc[idx].to_dict())

    # Filter cluster hanya yang memiliki jumlah lagu >= min_cluster_size
    filtered_clusters = {k: v for k, v in clusters.items() if len(v) >= min_cluster_size}
    return filtered_clusters


def find_audio_feature_duplicates(df, threshold=0.05):
    audio_features_cols = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness']
    available_features = [f for f in audio_features_cols if f in df.columns]

    if not available_features:
        print("Audio features tidak tersedia, lewati pencarian duplikat berdasarkan audio features.")
        return pd.DataFrame()

    duplicates = []
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            row1 = df.iloc[i]
            row2 = df.iloc[j]
            features1 = row1[available_features].dropna()
            features2 = row2[available_features].dropna()
            if len(features1) == len(features2) and len(features1) > 0:
                diff = abs(features1 - features2).mean()
                if diff < threshold:
                    duplicates.append({
                        'Track 1': row1['name'],
                        'Artist 1': row1['artists'],
                        'Track 2': row2['name'],
                        'Artist 2': row2['artists'],
                        'Avg Feature Diff': f"{diff:.4f}"
                    })
    return pd.DataFrame(duplicates)

def find_different_versions(df):
    versions = df[df.duplicated(subset=['spotify_id'], keep=False)]
    return versions.sort_values(by=['spotify_id', 'added_at'])

def generate_statistics(df):
    top_artists = df['artists'].value_counts().head(5)
    df['release_year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year
    top_years = df['release_year'].value_counts().dropna().head(5)
    total_duration_ms = df['duration_ms'].sum()
    total_duration_mins = total_duration_ms / (1000 * 60)
    total_duration_hrs = total_duration_mins / 60

    print("\n--- Statistik Keseluruhan ---")
    print(f"5 Artis Paling Sering Disukai:\n{top_artists}")
    print(f"\n5 Tahun Rilis Paling Populer:\n{top_years}")
    print(f"\nDurasi total semua lagu: {total_duration_hrs:.2f} jam ({total_duration_mins:.0f} menit)")
    print(f"Jumlah total lagu: {len(df)}")
    print(f"Jumlah artis unik: {df['artists'].nunique()}")

    return top_artists, top_years