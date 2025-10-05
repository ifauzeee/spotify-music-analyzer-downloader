import pandas as pd
from fuzzywuzzy import fuzz
from collections import defaultdict, Counter
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
from .config import get_config_value

def clean_title(title):
    common_words = ['feat', 'ft', 'remix', 'remastered', 'live', 'acoustic', 'version', 'edit', 'original', 'radio', 'mix']
    title_lower = title.lower()
    for word in common_words:
        title_lower = title_lower.replace(f' {word} ', ' ').replace(f'({word})', ' ').replace(f'[{word}]', ' ')
    cleaned = re.sub(r'[^a-z0-9\s]', ' ', title_lower)
    return ' '.join(cleaned.split())

def find_exact_duplicates(df):
    return df[df.duplicated(subset=['name', 'artists'], keep=False)]

def find_similar_titles_enhanced(df):
    threshold = get_config_value('Analysis', 'similarity_threshold')
    similar_pairs = []
    df_copy = df.copy()
    df_copy['cleaned_name'] = [clean_title(t) for t in df_copy['name']]

    for i in range(len(df_copy)):
        for j in range(i + 1, len(df_copy)):
            r1 = df_copy.iloc[i]; r2 = df_copy.iloc[j]
            ratio = fuzz.token_set_ratio(r1['cleaned_name'], r2['cleaned_name'])
            if ratio >= threshold:
                similar_pairs.append({'Track 1': r1['name'], 'Artist 1': r1['artists'], 'Track 2': r2['name'], 'Artist 2': r2['artists'], 'Match (%)': ratio})
    return pd.DataFrame(similar_pairs)

def group_similar_tracks(df):
    threshold = get_config_value('Analysis', 'similarity_threshold')
    df_copy = df.copy()
    df_copy['cleaned_name'] = [clean_title(t) for t in df_copy['name']]
    titles = df_copy['cleaned_name'].tolist()
    if len(titles) < 2: return {}

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(titles)
    dist_mat = 1 - cosine_similarity(tfidf_matrix)
    model = AgglomerativeClustering(n_clusters=None, linkage='average', distance_threshold=1 - (threshold / 100.0), metric='precomputed')
    labels = model.fit_predict(dist_mat)
    
    clusters = defaultdict(list)
    for idx, label in enumerate(labels):
        clusters[label].append(df_copy.iloc[idx].to_dict())
    return {k: v for k, v in clusters.items() if len(v) >= 2}

def find_different_versions(df):
    return df[df.duplicated(subset=['spotify_id'], keep=False)].sort_values(by=['spotify_id', 'added_at'])

def generate_statistics(df):
    df_copy = df.dropna(subset=['artists_list']).copy()
    all_artists = [artist for sublist in df_copy['artists_list'] for artist in sublist]
    top_artists = pd.Series(Counter(all_artists)).sort_values(ascending=False).head(5)
    df_copy['release_year'] = pd.to_datetime(df_copy['release_date'], errors='coerce').dt.year
    top_years = df_copy['release_year'].value_counts().dropna().astype(int).head(5)
    unique_artists = len(set(all_artists))
    return {
        "top_artists": top_artists, "top_years": top_years,
        "total_duration_hrs": df_copy['duration_ms'].sum() / 3600000,
        "total_tracks": len(df_copy), "unique_artists": unique_artists
    }

def generate_taste_profile(df):
    features = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness']
    available = [f for f in features if f in df.columns and pd.api.types.is_numeric_dtype(df[f]) and df[f].notna().any()]
    if not available:
        return None
    return df[available].mean().to_dict()

def analyze_genres(df, artist_genre_map):
    if 'artist_ids' not in df.columns: return []
    genre_counter = Counter(g for sublist in df['artist_ids'].dropna() for aid in sublist for g in artist_genre_map.get(aid, []))
    return genre_counter.most_common(10)