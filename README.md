# YouTube Downloader

A modern Python CLI tool for downloading YouTube videos and playlists with concurrent downloads, audio-only support, and robust error handling.

## Features
- Download single videos or entire playlists.
- Save playlists to a folder named after the playlist title.
- Prefix playlist video filenames with indices (e.g., `01_video.mp4`).
- Support for concurrent downloads to speed up playlist processing.
- Audio-only downloads in MP4 or MP3 format (requires `ffmpeg` for MP3).
- Automatic retry of failed downloads.
- Detailed download summary with success and failure reports.
- Configuration file support for default settings.
- Professional CLI with `click` for a polished user experience.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/smithded/youtube-downloader.git
   cd youtube-downloader
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Install the package:
   ```bash
   pip install .
   ```

5. (Optional) Install `ffmpeg` for MP3 conversion:
   - On Ubuntu: `sudo apt-get install ffmpeg`
   - On macOS: `brew install ffmpeg`
   - On Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

6. (Optional) Create a configuration file:
   ```bash
   cp config.yaml.example ~/.yt_downloader.yaml
   ```

## Running the CLI

- Directly from source (in virtual environment):
  ```bash
  python -m youtube_downloader <url> [options]
  ```
- After installation (as a command):
  ```bash
  youtube-downloader <url> [options]
  ```

## Usage Examples

- Download a playlist with default settings:
  ```bash
  python -m youtube_downloader https://youtube.com/playlist?list=... -o downloads -q 720p
  ```

- Download audio-only in MP3 format with 2 concurrent downloads:
  ```bash
  python -m youtube_downloader https://youtube.com/playlist?list=... --audio-only --audio-format mp3 --max-concurrent 2
  ```

- Retry failed downloads with 2 attempts:
  ```bash
  python -m youtube_downloader https://youtube.com/watch?v=... --retry --retry-attempts 2
  ```

## Options

- `-o, --output`: Output directory (default: `downloads`).
- `-q, --quality`: Video quality (`highest`, `720p`, `480p`, `360p`).
- `--prefix-index/--no-prefix-index`: Prefix playlist filenames with index.
- `--retry/--no-retry`: Retry failed downloads.
- `--retry-attempts`: Number of retry attempts.
- `--max-concurrent`: Maximum concurrent downloads.
- `--audio-only/--no-audio-only`: Download audio only.
- `--audio-format`: Audio format (`mp4`, `mp3`).
- `--version`: Show version.
- `-h, --help`: Show help.

## Configuration

Create `~/.yt_downloader.yaml` to set defaults:

```yaml
output: downloads
quality: 720p
prefix_index: true
retry: true
retry_attempts: 2
max_concurrent: 4
audio_only: false
audio_format: mp4
```

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/awesome-feature`).
3. Commit changes (`git commit -m 'Add awesome feature'`).
4. Push to the branch (`git push origin feature/awesome-feature`).
5. Open a pull request.

Run tests with:
```bash
pytest
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

Built with [pytubefix](https://github.com/JuanBindez/pytubefix), [tqdm](https://github.com/tqdm/tqdm), and [click](https://github.com/pallets/click).
