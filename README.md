# 🎵 Spotify Music Analyzer & Downloader 🎶

<p align="center">
  <img src="https://www.svgrepo.com/show/475675/spotify-logo.svg" alt="Spotify Logo" width="100" height="100">
  <br>
  <strong>A Python Tool for Analyzing Your Spotify Tastes & Downloading Tracks</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-prerequisites">Prerequisites</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-important-legal-notice">Legal Notice</a> •
  <a href="#-project-structure">Structure</a>
</p>

---

## 📋 Description

**Spotify Music Analyzer & Downloader** is a command-line Python project designed to help you **analyze your Spotify liked tracks** and **download tracks from Spotify URLs**. This tool offers deep insights into your musical tastes and provides options for saving tracks locally (with strict legal warnings).

---

## ⭐ Key Features

### 🔍 **Liked Tracks Analysis**
*   **Fetch Data:** Safely retrieves all your liked tracks from your Spotify account.
*   **Duplicate Detection:** Identifies identical tracks (same name and artist) within your collection.
*   **Smart Title Matching:** Finds tracks with similar or nearly identical titles using fuzzy matching, helping spot alternate versions or typos.
*   **Track Grouping:** Automatically groups similar tracks using text-based clustering techniques (TF-IDF).
*   **In-depth Statistics:** Provides summary statistics like top artists, most popular release years, and total collection duration.
*   **Different Versions:** Finds the same track (based on Spotify ID) but from different albums (e.g., live, acoustic, remastered).

### 📥 **Downloader Feature**
*   **Format Support:** Supports various audio formats like **MP3 (lossy)**, **FLAC (lossless)**, and **M4A (lossy)**.
*   **Quality Control:** For lossy formats, you can select bitrate quality (e.g., 320kbps, 256kbps).
*   **From Spotify URL:** Downloads tracks, albums, or playlists directly from a valid Spotify URL.
*   **From CSV:** Downloads a list of previously analyzed tracks from the `outputs/my_liked_tracks.csv` file.
*   **File Information:** Displays track metadata (title, artist, album) and **estimated and actual file sizes** after download completes.

---

## ⚠️ Important Legal Notice

> [!CAUTION]
> The **Downloader** feature in this project **likely violates the Spotify Terms of Service** and **potentially copyright laws**. Spotify is a legal streaming service, and downloading its content without explicit permission is generally illegal.
>
> Use this feature **solely for personal, experimental, and educational purposes**. Do **not** use it for distribution, commercial gain, or other illegal activities.
> The author **is not responsible** for any misuse of this feature. Spotify may change its API or systems at any time, potentially breaking this feature. Using the official **Spotify Premium offline mode** is recommended for legal offline listening.

---

## 🧰 Prerequisites

*   **Python:** Version `3.8` or higher must be installed on your system.
*   **Spotify Account:** You need a Spotify account (Premium or Free) to access your liked tracks.
*   **Spotify Developer Application:** You need to create an app on the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) to obtain API credentials.

---

## 🚀 Installation

1.  **Clone the Repository:**
    Open your terminal or command prompt and run:
    ```bash
    git clone https://github.com/ifauzeee/spotify-music-analyzer-downloader.git
    cd spotify-music-analyzer-downloader
    ```

2.  **(Optional but Recommended) Create a Virtual Environment:**
    This helps isolate project dependencies.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # Or on Windows:
    # venv\Scripts\activate
    ```

3.  **Install Python Dependencies:**
    Ensure your virtual environment is active, then install all required packages.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Spotify Credentials:**
    *   Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
    *   Log in and create a new app.
    *   Add `http://127.0.0.1:8888/callback` to the **Redirect URIs** list.
    *   Note down your **Client ID** and **Client Secret**.
    *   Create a new file named `.env` in the project's root directory (`spotify-music-analyzer-downloader/.env`).
    *   Add your credentials to the `.env` file in the following format:
        ```env
        SPOTIPY_CLIENT_ID=YOUR_SPOTIFY_CLIENT_ID_HERE
        SPOTIPY_CLIENT_SECRET=YOUR_SPOTIFY_CLIENT_SECRET_HERE
        SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
        ```
    *   **Important:** Never upload the `.env` file to a public repository. The included `.gitignore` file should already handle this.

---

## 🎮 Usage

1.  **Activate the Virtual Environment (if you created one):**
    ```bash
    source venv/bin/activate  # On Linux/macOS
    # Or on Windows:
    # venv\Scripts\activate
    ```

2.  **Run the Main Script:**
    ```bash
    python main.py
    ```

3.  **Follow the Interactive Menu:**
    *   **Analyzer:** Choose this to fetch liked track data (if not already present) and run all analysis features (duplicates, similarities, statistics).
    *   **Downloader:** Choose this to open the downloader submenu.
        *   **Download from CSV:** Download tracks from the `outputs/my_liked_tracks.csv` file.
        *   **Download from Spotify URL:** Download a track, album, or playlist from a Spotify URL.

---

## 📁 Project Structure

```
spotify-music-analyzer-downloader/
│
├── .env                 # (NOT COMMITTED) Your Spotify credentials
├── .gitignore           # Files/dirs ignored by Git
├── README.md            # This documentation file
├── requirements.txt     # Python dependency list
├── main.py              # Main application entry point
├── logs/                # (Optional) For application logs
├── outputs/             # Output data (CSV, downloaded files)
│   ├── my_liked_tracks.csv # Saved liked tracks data
│   └── downloads/       # Default download location
└── src/                 # Main source code
    ├── __init__.py
    ├── auth.py          # Spotify API authentication
    ├── data.py          # Fetches & processes track data
    ├── analysis.py      # Analysis functions
    ├── visualization.py # (Present in code, not used in current main.py)
    └── downloader.py    # Download functions
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. This license applies to the **source code** of this project. It **grants no rights** to the music content that might be downloaded using this tool, which remains under Spotify's and the artists' copyright.

---

<p align="center">
  <em>Made for personal exploration and learning.</em>
</p>
```