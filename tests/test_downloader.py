import pytest
from pathlib import Path
from youtube_downloader.downloader import YouTubeDownloader

def test_create_output_directory(tmp_path: Path):
    downloader = YouTubeDownloader(
        output_dir=tmp_path / "test",
        quality="highest",
        audio_only=False,
        audio_format="mp4",
        prefix_index=True,
        retry=False,
        retry_attempts=1,
        max_concurrent=4
    )
    output_dir = downloader.create_output_directory(tmp_path / "test")
    assert output_dir.exists()
    assert output_dir.is_dir()
