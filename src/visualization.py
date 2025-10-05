# src/visualization.py
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import os

# Buat folder outputs jika belum ada
os.makedirs('outputs', exist_ok=True)

def plot_artist_counts(top_artists):
    if top_artists.empty:
        print("Tidak ada data artis untuk divisualisasikan.")
        return
    plt.figure(figsize=(10, 6))
    plt.bar(top_artists.index, top_artists.values, color='skyblue')
    plt.title('5 Artis Paling Sering Disukai')
    plt.xlabel('Artis')
    plt.ylabel('Jumlah Lagu')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('outputs/top_artists.png')
    plt.show()

def plot_release_years(top_years):
    if top_years.empty:
        print("Tidak ada data tahun rilis untuk divisualisasikan.")
        return
    plt.figure(figsize=(10, 6))
    plt.bar(top_years.index.astype(int), top_years.values, color='lightcoral')
    plt.title('5 Tahun Rilis Paling Populer')
    plt.xlabel('Tahun')
    plt.ylabel('Jumlah Lagu')
    plt.tight_layout()
    plt.savefig('outputs/top_years.png')
    plt.show()

def plot_audio_features(df):
    audio_features_cols = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness']
    available_features = [f for f in audio_features_cols if f in df.columns]
    averages = [df[f].mean() for f in available_features]

    if not averages:
        print("Tidak ada nilai audio features untuk divisualisasikan.")
        return

    plt.figure(figsize=(10, 6))
    plt.bar(available_features, averages, color='lightgreen')
    plt.title('Rata-rata Audio Features')
    plt.xlabel('Feature')
    plt.ylabel('Nilai Rata-rata')
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig('outputs/audio_features.png')
    plt.show()

def create_wordcloud(df):
    text = ' '.join(df['name'].dropna().tolist())
    if not text.strip():
        print("Tidak ada teks untuk membuat word cloud.")
        return

    wordcloud = WordCloud(width=800, height=400, background_color='white', max_words=100).generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud dari Judul Lagu')
    plt.tight_layout()
    plt.savefig('outputs/wordcloud.png')
    plt.show()