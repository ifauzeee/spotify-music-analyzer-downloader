# src/downloader.py
import subprocess
from rich.console import Console
from rich.table import Table
import os
import math # Untuk estimasi ukuran
import glob # Untuk mencari file yang baru diunduh

console = Console()

def get_track_metadata_from_url(spotify_url: str):
    """Mengambil metadata (judul, artis, album, durasi) dari URL Spotify menggunakan spotdl."""
    try:
        from .auth import get_spotify_client
        sp = get_spotify_client()
        import re
        match = re.search(r'/(track|album|playlist)/([A-Za-z0-9]+)', spotify_url)
        if not match or match.group(1) != 'track':
            console.print("[bold red]❌ URL bukan track Spotify.[/bold red]")
            return None
        track_id = match.group(2)

        track_info = sp.track(track_id)
        metadata = {
            'name': track_info['name'],
            'artists': ', '.join([artist['name'] for artist in track_info['artists']]),
            'album': track_info['album']['name'],
            'duration_ms': track_info['duration_ms'],
            'release_date': track_info['album']['release_date'],
            'external_url': track_info['external_urls']['spotify'],
        }
        return metadata
    except Exception as e:
        console.print(f"[bold red]❌ Gagal mengambil metadata: {e}[/bold red]")
        return None

def estimate_file_size_mb(duration_ms, bitrate_kbps=320):
    """Mengestimasi ukuran file dalam MB berdasarkan durasi (ms) dan bitrate (kbps)."""
    duration_seconds = duration_ms / 1000.0
    size_bits = duration_seconds * bitrate_kbps * 1000 # kbps -> bps
    size_bytes = size_bits / 8
    size_mb = size_bytes / (1024 * 1024)
    return round(size_mb, 2)

def display_track_info(metadata, format_opt, quality):
    """Menampilkan informasi track dalam tabel."""
    table = Table(title="Informasi Lagu yang Akan Diunduh")
    table.add_column("Detail", style="bold cyan")
    table.add_column("Info", style="magenta")

    table.add_row("Judul", metadata['name'])
    table.add_row("Artis", metadata['artists'])
    table.add_row("Album", metadata['album'])
    table.add_row("Tanggal Rilis", metadata['release_date'])
    table.add_row("Durasi", f"{metadata['duration_ms'] / 1000 / 60:.2f} menit")
    table.add_row("Format", format_opt.upper())
    table.add_row("Kualitas", quality.upper() if quality != "best" else "Tertinggi Tersedia")
    # Estimasi ukuran untuk MP3 320kbps sebagai contoh
    est_bitrate = 320 if quality == "best" or quality not in ["320k", "256k", "192k", "128k"] else int(quality[:-1])
    est_size = estimate_file_size_mb(metadata['duration_ms'], est_bitrate)
    table.add_row("Estimasi Ukuran File (MP3 320kbps)", f"{est_size} MB")
    # Untuk format lain seperti FLAC, ukuran bisa sangat bervariasi, estimasi kasar
    if format_opt.lower() == 'flac':
        est_size_flac = est_size * 3 # Gunakan faktor 3 sebagai estimasi tengah
        table.add_row("Estimasi Ukuran File (FLAC)", f"~{est_size_flac} MB (bisa lebih besar/kecil)")

    console.print(table)


def download_track_from_spotify_url_with_options(spotify_url: str, output_dir: str = "downloads", format_opt: str = "mp3", quality: str = "best"):
    """
    Mengunduh lagu dari URL Spotify menggunakan spotdl dengan opsi format dan kualitas.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Ambil metadata sebelum mengunduh
    metadata = get_track_metadata_from_url(spotify_url)
    if not metadata:
        return # Gagal mengambil metadata, hentikan proses

    # Tampilkan info sebelum download
    display_track_info(metadata, format_opt, quality)

    try:
        # Catat waktu sebelum download
        import time
        download_start_time = time.time()

        cmd = ["spotdl", spotify_url, "--output", output_dir, "--format", format_opt]
        if format_opt in ["mp3", "m4a", "opus"]:
            if quality != "best" and quality in ["320k", "256k", "192k", "128k"]:
                 cmd.extend(["--ffmpeg-args", f"-b:a {quality}"])

        console.print(f"\n[bold blue]Mengunduh dari: {spotify_url}[/bold blue]")
        console.print(f"[bold blue]Format: {format_opt}, Kualitas (jika berlaku): {quality}[/bold blue]")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # --- Tambahkan Pengecekan Ukuran File ---
        # SpotDL biasanya menamai file berdasarkan "{artist} - {title}.{format}"
        # Kita buat nama file yang diharapkan
        # Hapus karakter yang tidak valid untuk nama file
        import re
        safe_artist = re.sub(r'[<>:"/\\|?*]', '_', metadata['artists'])
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', metadata['name'])
        expected_filename = f"{safe_artist} - {safe_title}.{format_opt}"
        expected_file_path = os.path.join(output_dir, expected_filename)

        # Periksa apakah file benar-benar dibuat dan dapatkan ukurannya
        if os.path.exists(expected_file_path):
            file_size_bytes = os.path.getsize(expected_file_path)
            file_size_mb = file_size_bytes / (1024 * 1024) # Konversi ke MB
            file_size_mb_rounded = round(file_size_mb, 2)

            console.print(f"[bold green]✅ Berhasil mengunduh: {metadata['name']} (oleh {metadata['artists']})[/bold green]")
            console.print(f"[bold blue]Ukuran File Asli: {file_size_mb_rounded} MB[/bold blue]")
        else:
            # Jika file tidak ditemukan dengan nama yang diharapkan, coba cari file terbaru di folder
            # Ini untuk kasus jika spotdl mengubah nama (misalnya menambahkan ID)
            list_of_files = glob.glob(os.path.join(output_dir, f"*.{format_opt}"))
            if list_of_files:
                latest_file = max(list_of_files, key=os.path.getctime)
                # Pastikan file ini dibuat setelah proses download dimulai
                if os.path.getctime(latest_file) >= download_start_time:
                    file_size_bytes = os.path.getsize(latest_file)
                    file_size_mb = file_size_bytes / (1024 * 1024)
                    file_size_mb_rounded = round(file_size_mb, 2)
                    actual_filename = os.path.basename(latest_file)

                    console.print(f"[bold green]✅ Berhasil mengunduh: {actual_filename}[/bold green]")
                    console.print(f"[bold blue]Ukuran File Asli: {file_size_mb_rounded} MB[/bold blue]")
                else:
                    console.print(f"[bold green]✅ Berhasil mengunduh: {metadata['name']} (oleh {metadata['artists']})[/bold green]")
                    console.print(f"[bold yellow]⚠️  File ditemukan, tetapi tidak bisa mendapatkan ukuran secara otomatis.[/bold yellow]")
            else:
                 console.print(f"[bold green]✅ Berhasil mengunduh: {metadata['name']} (oleh {metadata['artists']})[/bold green]")
                 console.print(f"[bold yellow]⚠️  File output tidak ditemukan di {output_dir}.[/bold yellow]")
        # --- Selesai Tambahkan Pengecekan Ukuran File ---

        # print(result.stdout)
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]❌ Gagal mengunduh {spotify_url}. Error: {e}[/bold red]")
        # print(e.stderr)
    except FileNotFoundError:
        console.print("[bold red]❌ spotdl tidak ditemukan. Pastikan sudah diinstal.[/bold red]")

def download_tracks_from_list_with_options(track_urls: list, output_dir: str = "downloads", format_opt: str = "mp3", quality: str = "best"):
    """
    Mengunduh daftar lagu dari list URL Spotify dengan opsi format dan kualitas.
    """
    os.makedirs(output_dir, exist_ok=True)
    console.print(f"[bold blue]Memulai pengunduhan {len(track_urls)} lagu...[/bold blue]")
    console.print(f"[bold blue]Format: {format_opt}, Kualitas (jika berlaku): {quality}[/bold blue]")
    for url in track_urls:
        if "open.spotify.com/track/" not in url:
            console.print(f"[bold red]❌ URL tidak valid (bukan track): {url}[/bold red]")
            continue
        download_track_from_spotify_url_with_options(url, output_dir, format_opt, quality)
    console.print(f"[bold green]✅ Selesai mengunduh {len(track_urls)} lagu.[/bold green]")

def download_from_list_csv(df, output_dir: str = "downloads", format_opt: str = "mp3", quality: str = "best", limit=None):
    """Mengunduh dari DataFrame (CSV) dengan opsi."""
    urls = df['external_url'].tolist()
    if limit:
        urls = urls[:limit]
    download_tracks_from_list_with_options(urls, output_dir, format_opt, quality)
