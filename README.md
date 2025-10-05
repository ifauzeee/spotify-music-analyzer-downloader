<p align="center">
  <img src="assets/image.png" alt="Project Banner" width="800">
</p>

<h1 align="center">Spotify Music Analyzer & Downloader</h1>

<p align="center">
  A sophisticated Flask web application to analyze your Spotify music library, discover insights about your listening habits, and download tracks for offline use.
</p>

<p align="center">
    <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python" alt="Python Version">
    <img src="https://img.shields.io/badge/Flask-2.x-black?style=for-the-badge&logo=flask" alt="Flask">
    <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
  <a href="#-about-the-project">About</a> •
  <a href="#-key-features">Features</a> •
  <a href="#-live-demo">Live Demo</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-project-structure">Structure</a> •
  <a href="#-legal-notice">Legal Notice</a>
</p>

---

## 📖 About The Project

This project transforms the original command-line tool into a full-featured, modern web application using Flask. It provides a seamless user experience for securely authenticating with Spotify, running complex music analysis in the background, and downloading tracks directly from your browser. The entire interface is designed to be clean, intuitive, and responsive, with a focus on providing powerful features in a simple package.

The application leverages background threading to handle long-running processes like fetching thousands of songs or downloading large files, ensuring the user interface remains responsive. A live progress bar keeps the user informed, creating a smooth and interactive experience from start to finish.

---

## ⭐ Key Features

### 🔍 Analyzer

-   **Comprehensive Statistics:** Get a full breakdown of your music library, including total tracks, unique artists, and total listening duration.
-   **Top Insights:** Discover your most-played artists, most common release years, and dominant genres.
-   **Duplicate Detection:** Easily find and manage exact duplicate tracks (same name and artist) in your liked songs or playlists.
-   **Version Discovery:** Identifies different versions of the same song (e.g., studio, live, acoustic, remastered) that share the same Spotify ID.

### 📥 Downloader

-   **Direct URL Downloading:** Download any Spotify track by simply pasting its URL.
-   **Format Selection:** Choose from multiple audio formats, including high-quality **MP3** and lossless **FLAC**.
-   **Quality Control:** Select the desired bitrate for lossy formats to balance file size and audio quality.

### 🌐 Web Interface

-   **Secure Spotify OAuth:** A seamless and secure login flow that connects to your Spotify account without ever storing your password.
-   **Background Task Processing:** Long-running analysis and download tasks are executed in the background, so your browser never freezes or times out.
-   **Live Progress Bar:** A real-time loading bar shows the status of your task, from fetching data to completion.
-   **Modern UI:** A clean, dark-themed, and minimalist interface designed for ease of use.

---

## 📸 Live Demo

#### **Analysis Results Page**
The main results page, displaying a clean, table-based layout of your music statistics.
![Analysis Results](assets/Screenshot%202025-10-06%20at%2002-48-32%20Spotify%20Music%20Analyzer.png)

#### **Downloader Page**
The simple and intuitive interface for downloading tracks.
![Download Page](assets/Screenshot%202025-10-06%20at%2002-47-35%20Spotify%20Music%20Analyzer.png)

#### **Download Success Notification**
The loading page transforms to show a download link once the background process is complete.
![Download Success](assets/Screenshot%202025-10-06%20at%2002-46-39%20Spotify%20Music%20Analyzer.png)

---

## 🛠️ Tech Stack

This project is built with a modern Python web stack:

-   **Backend:** [Flask](https://flask.palletsprojects.com/)
-   **Spotify Integration:** [Spotipy](https://spotipy.readthedocs.io/)
-   **Data Manipulation:** [Pandas](https://pandas.pydata.org/)
-   **Audio Downloading:** [spotdl](https://github.com/spotdl/spotify-downloader)
-   **Fuzzy Matching:** [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy)
-   **Frontend:** HTML, CSS, Jinja2 Templating

---

## 🚀 Getting Started

Follow these steps to set up and run the project on your local machine.

### Prerequisites

-   **Python 3.8+**
-   **A Spotify Account** (Free or Premium)
-   **Git** (for cloning the repository)

### Installation

1.  **Clone the Repository**
    ```sh
    https://github.com/ifauzeee/spotify-music-analyzer-downloader.git
    cd spotify-music-analyzer-downloader
    ```

2.  **Create and Activate a Virtual Environment**
    This isolates the project's dependencies from your system.
    ```sh
    # Create the environment
    python -m venv venv

    # Activate on Windows (PowerShell)
    .\venv\Scripts\Activate.ps1

    # Activate on macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    Install all required Python packages from the `requirements.txt` file.
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set Up Spotify API Credentials**
    You need to register an application on the Spotify Developer Dashboard to get API keys.
    
    a. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and log in.
    
    b. Click **"Create App"**. Give it a name and description.
    
    c. Once created, you will see your **Client ID** and **Client Secret**. Copy these.
    
    d. Click **"Edit Settings"**. In the **Redirect URIs** field, add the following URL exactly:
       ```
       [http://127.0.0.1:8888/callback](http://127.0.0.1:8888/callback)
       ```
    e. Click **"Save"**.

5.  **Configure Environment Variables**
    Create a file named `.env` in the root directory of the project. This file will securely store your API keys.
    
    Copy the following content into your `.env` file and replace the placeholder values with your actual credentials.
    ```env
    # .env
    SPOTIPY_CLIENT_ID="YOUR_CLIENT_ID_HERE"
    SPOTIPY_CLIENT_SECRET="YOUR_CLIENT_SECRET_HERE"
    SPOTIPY_REDIRECT_URI="[http://127.0.0.1:8888/callback](http://127.0.0.1:8888/callback)"
    ```
    > **Note:** The `.gitignore` file is already configured to prevent this file from being uploaded to GitHub.

---

## 🎮 Usage

1.  **Activate Your Virtual Environment**
    ```sh
    .\venv\Scripts\Activate.ps1
    ```

2.  **Run the Flask Application**
    ```sh
    flask run --port=8888
    ```

3.  **Open Your Browser**
    -   Navigate to `http://127.0.0.1:8888/`.
    -   The application will automatically redirect you to the Spotify login page for authentication.
    -   After you grant permission, you will be redirected back to the application's home page, fully logged in.
    -   From there, you can choose to analyze your liked songs, a playlist, or go to the downloader page.

---

## 📁 Project Structure

````

spotify-music-analyzer/
│
├── .env                 \# (Ignored by Git) Your Spotify credentials
├── .gitignore           \# Files and directories to be ignored by Git
├── README.md            \# This file
├── requirements.txt     \# Python dependencies
├── app.py               \# The core Flask application logic and routes
├── config.ini           \# Configuration for analysis parameters
│
├── src/                 \# Source code for backend logic
│   ├── analysis.py      \# Functions for data analysis
│   ├── auth.py          \# Initial Spotipy client configuration
│   ├── config.py        \# Helper to read config.ini
│   ├── data.py          \# Functions for fetching data from Spotify API
│   └── database.py      \# SQLite database and caching logic
│
├── static/              \# Static web files
│   └── style.css
│   └── downloads/       \# (Created automatically) Default location for downloads
│
└── templates/           \# HTML templates for the web interface
├── index.html
├── layout.html
├── downloader.html
├── loading.html
└── results.html

```


## ⚖️ Legal Notice

> [!CAUTION]
> The **Downloader** feature in this project likely violates the Spotify Terms of Service and potentially copyright laws. Spotify is a legal streaming service, and downloading its content without explicit permission is generally not permitted.
>
> This feature should be used **solely for personal, experimental, and educational purposes**. Do not use it for distribution, commercial gain, or other illegal activities. The author is not responsible for any misuse of this feature.
>
> The officially supported method for offline listening is through **Spotify Premium**.

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for improvements or find a bug, please feel free to open an issue or submit a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more information. This license applies to the **source code** of this project and grants no rights to any music content downloaded with this tool.