# main.py
from rich.console import Console
from rich.table import Table
import pandas as pd
import os
import re # Untuk validasi URL

# Import dari modul src
from src.data import get_all_liked_tracks, extract_track_info, get_audio_features
from src.analysis import (
    find_exact_duplicates, find_similar_titles_enhanced, group_similar_tracks,
    find_audio_feature_duplicates, find_different_versions, generate_statistics
)
# from src.visualization import plot_artist_counts, plot_release_years, plot_audio_features, create_wordcloud # <-- Di-comment atau dihapus
from src.downloader import download_from_list_csv, download_track_from_spotify_url_with_options # Import fungsi download

console = Console()

def display_results(title, df, columns):
    if df.empty:
        console.print(f"✅ [bold green]{title}[/bold green]: Tidak ditemukan.")
        return

    table = Table(title=title)
    for col in columns:
        table.add_column(col, style="cyan" if "Match" in col else "magenta" if "Track" in col else "green")

    for _, row in df.iterrows():
        table.add_row(*[str(row[col]) for col in columns])

    console.print(table)

def display_grouped_tracks(clusters):
    console.print("\n[bold yellow]🔗 Hasil Pengelompokan Lagu Mirip (2 lagu atau lebih):[/bold yellow]")
    for cluster_id, tracks in clusters.items():
        num_tracks = len(tracks)
        if num_tracks >= 2: # Sudah difilter, tapi jaga-juga
            table = Table(title=f"Cluster {cluster_id} ({num_tracks} Lagu)")
            table.add_column("Judul", style="magenta")
            table.add_column("Artis", style="green")
            # Batasi jumlah lagu yang ditampilkan dalam satu cluster
            display_limit = 10 # Misalnya, tampilkan maksimal 10 lagu pertama
            for track in tracks[:display_limit]:
                table.add_row(track['name'], track['artists'])
            if num_tracks > display_limit:
                 table.add_row(f"... dan {num_tracks - display_limit} lagu lainnya", "")
            console.print(table)
        else:
            # Cluster dengan kurang dari 2 lagu diabaikan karena difilter
            pass

def load_data():
    """Memuat data lagu yang disukai dari file CSV."""
    if os.path.exists('outputs/my_liked_tracks.csv'):
        console.print("[bold blue]📊 Memuat data dari file 'outputs/my_liked_tracks.csv'...[/bold blue]")
        return pd.read_csv('outputs/my_liked_tracks.csv')
    else:
        console.print("[bold yellow]⚠️ File 'outputs/my_liked_tracks.csv' tidak ditemukan.[/bold yellow]")
        return None

def get_format_quality_options():
    """Mendapatkan input format dan kualitas dari pengguna."""
    console.print("\n[bold yellow]Pilih format file:[/bold yellow]")
    console.print("1. mp3 (Lossy, ukuran kecil, kompatibel)")
    console.print("2. flac (Lossless, ukuran besar, kualitas asli)")
    console.print("3. m4a (Lossy, ukuran kecil, kompatibel Apple)")
    format_choice = console.input("[bold cyan]Masukkan pilihan (1-3, default: mp3): [/bold cyan]") or "1"
    format_map = {"1": "mp3", "2": "flac", "3": "m4a"}
    format_opt = format_map.get(format_choice, "mp3")

    quality = "best" # Default
    if format_opt in ["mp3", "m4a", "opus"]:
        console.print(f"\n[bold yellow]Pilih kualitas untuk {format_opt.upper()} (hanya berpengaruh pada format lossy):[/bold yellow]")
        console.print("1. best (Tertinggi yang tersedia, biasanya ~320kbps)")
        console.print("2. 320k")
        console.print("3. 256k")
        console.print("4. 192k")
        console.print("5. 128k")
        quality_choice = console.input("[bold cyan]Masukkan pilihan (1-5, default: best): [/bold cyan]") or "1"
        quality_map = {"1": "best", "2": "320k", "3": "256k", "4": "192k", "5": "128k"}
        quality = quality_map.get(quality_choice, "best")
    return format_opt, quality

def run_analyzer():
    """Menjalankan semua fungsi analisis."""
    console.print("\n[bold blue]🎵 Memulai proses Analisis...[/bold blue]")
    df = load_data()
    if df is None:
        console.print("[bold yellow]⚠️ Data tidak ditemukan. Mengambil data dari Spotify...[/bold yellow]")
        tracks = get_all_liked_tracks()
        console.print(f"[bold green]✅ Ditemukan {len(tracks)} lagu yang kamu sukai.[/bold green]")
        df_raw = pd.DataFrame(extract_track_info(tracks))
        df_with_features = get_audio_features(df_raw)
        df = df_with_features

        # Simpan data jika diambil dari Spotify
        os.makedirs('outputs', exist_ok=True) # Folder outputs tetap dibuat untuk file CSV
        df.to_csv('outputs/my_liked_tracks.csv', index=False)
        console.print("\n💾 Data telah disimpan ke [bold yellow]outputs/my_liked_tracks.csv[/bold yellow]")

    # --- JALANKAN SEMUA ANALISIS ---
    console.print("\n[bold yellow]📊 Menampilkan Statistik Keseluruhan...[/bold yellow]")
    top_artists, top_years = generate_statistics(df)

    # --- KOMENTAR/REMOVE BARIS INI ---
    # console.print("\n[bold yellow]🎨 Membuat visualisasi...[/bold yellow]")
    # plot_artist_counts(top_artists)
    # plot_release_years(top_years)
    # plot_audio_features(df)
    # create_wordcloud(df)
    console.print("\n[bold yellow]🎨 Membuat visualisasi... DILEWATKAN.[/bold yellow]")

    console.print("\n[bold yellow]🔍 Mencari duplikasi nama dan artis...[/bold yellow]")
    dupes = find_exact_duplicates(df)
    display_results("Lagu Duplikat di Loved Tracks", dupes, ['name', 'artists', 'album', 'added_at'])

    console.print("\n[bold yellow]🔍 Mencari judul lagu yang mirip (versi pintar)...[/bold yellow]")
    similar = find_similar_titles_enhanced(df, threshold=85)
    display_results("Judul Mirip di Loved Tracks", similar, ['Track 1', 'Artist 1', 'Track 2', 'Artist 2', 'Match (%)'])

    console.print("\n[bold yellow]🔗 Mengelompokkan lagu-lagu mirip...[/bold yellow]")
    clusters = group_similar_tracks(df, threshold=85, min_cluster_size=2)
    display_grouped_tracks(clusters)

    console.print("\n[bold yellow]🎵 Mencari duplikat berdasarkan audio features...[/bold yellow]")
    audio_dupes = find_audio_feature_duplicates(df, threshold=0.05)
    display_results("Duplikat Berdasarkan Audio Features", audio_dupes, ['Track 1', 'Artist 1', 'Track 2', 'Artist 2', 'Avg Feature Diff'])

    console.print("\n[bold yellow]🔍 Mencari versi berbeda dari lagu yang sama...[/bold yellow]")
    versions = find_different_versions(df)
    display_results("Versi Berbeda dari Lagu Sama", versions, ['name', 'artists', 'album', 'added_at', 'spotify_id'])

    console.print("\n✅ [bold green]Proses Analisis Selesai.[/bold green]")

def run_downloader():
    """Menampilkan submenu downloader."""
    while True:
        console.print("\n[bold magenta]📥 Spotify Downloader[/bold magenta]")
        console.print("Pilih opsi download:")
        console.print("10. Download Lagu (dari file CSV)")
        console.print("11. Download Lagu (dari URL Spotify)")
        console.print("0. Kembali ke Menu Utama")

        choice = console.input("\n[bold cyan]Masukkan pilihan kamu (0, 10, 11): [/bold cyan]")

        if choice == '10':
            df = load_data()
            if df is None:
                console.print("[bold red]❌ Tidak ada data untuk diunduh. Silakan jalankan Analyzer terlebih dahulu atau pastikan file 'outputs/my_liked_tracks.csv' ada.[/bold red]")
                input("\nTekan Enter untuk kembali ke submenu downloader...")
                continue

            output_dir = console.input("[bold yellow]Masukkan nama folder output (default: 'downloads'): [/bold yellow]") or "downloads"
            try:
                limit_input = console.input("\n[bold yellow]Masukkan jumlah lagu yang ingin diunduh (tekan Enter untuk semua): [/bold yellow]")
                limit = int(limit_input) if limit_input.strip() else None
                format_opt, quality = get_format_quality_options()
                console.print(f"[bold blue]Memulai pengunduhan...[/bold blue]")
                download_from_list_csv(df, output_dir=output_dir, format_opt=format_opt, quality=quality, limit=limit)
            except ValueError:
                console.print("[bold red]❌ Input tidak valid. Harap masukkan angka.[/bold red]")
            except KeyboardInterrupt:
                console.print("\n[bold red]❌ Pengunduhan dibatalkan.[/bold red]")
            input("\nTekan Enter untuk kembali ke submenu downloader...")

        elif choice == '11':
            url = console.input("\n[bold yellow]Masukkan URL Spotify (track, album, playlist): [/bold yellow]")
            if not re.match(r'^https?://open\.spotify\.com/(intl-[a-z]{2}/)?(track|album|playlist)/[A-Za-z0-9]+(\?si=[A-Za-z0-9]+)?$', url, re.IGNORECASE):
                console.print("[bold red]❌ URL Spotify tidak valid. Harus berupa track, album, atau playlist.[/bold red]")
                input("\nTekan Enter untuk kembali ke submenu downloader...")
                continue

            output_dir = console.input("[bold yellow]Masukkan nama folder output (default: 'downloads'): [/bold yellow]") or "downloads"
            format_opt, quality = get_format_quality_options()
            download_track_from_spotify_url_with_options(url, output_dir=output_dir, format_opt=format_opt, quality=quality)
            input("\nTekan Enter untuk kembali ke submenu downloader...")

        elif choice == '0':
            console.print("\n🔙 Kembali ke menu utama...")
            break
        else:
            console.print("\n❌ [bold red]Pilihan tidak valid. Silakan coba lagi.[/bold red]")
            input("\nTekan Enter untuk kembali ke submenu downloader...")

def main_menu():
    """Menampilkan menu utama."""
    console.print("\n[bold magenta]🎵 Spotify Music Analyzer & Downloader 🎵[/bold magenta]")
    console.print("Pilih fitur utama:")
    console.print("1. Analyzer")
    console.print("2. Downloader")
    console.print("0. Keluar")

if __name__ == '__main__':
    while True:
        main_menu()
        choice = console.input("\n[bold cyan]Masukkan pilihan kamu (0-2): [/bold cyan]")

        if choice == '1':
            run_analyzer()
            input("\nTekan Enter untuk kembali ke menu utama...")
        elif choice == '2':
            run_downloader()
        elif choice == '0':
            console.print("\n👋 [bold green]Terima kasih telah menggunakan Spotify Music Analyzer![/bold green]")
            break
        else:
            console.print("\n❌ [bold red]Pilihan tidak valid. Silakan coba lagi.[/bold red]")
            input("\nTekan Enter untuk kembali ke menu utama...")
