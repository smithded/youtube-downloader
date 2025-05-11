import click
import logging
from pathlib import Path
from typing import Optional
from .downloader import YouTubeDownloader
from .config import load_config

__version__ = "1.0.0"

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("url")
@click.option(
    "-o", "--output",
    default=None,
    help="Output directory (default: from config or 'downloads')",
    type=click.Path()
)
@click.option(
    "-q", "--quality",
    default=None,
    type=click.Choice(["highest", "720p", "480p", "360p"]),
    help="Video quality (default: from config or 'highest')"
)
@click.option(
    "--prefix-index/--no-prefix-index",
    default=None,
    help="Prefix playlist filenames with index (default: from config or True)"
)
@click.option(
    "--retry/--no-retry",
    default=None,
    help="Retry failed downloads (default: from config or False)"
)
@click.option(
    "--retry-attempts",
    default=None,
    type=int,
    help="Number of retry attempts (default: from config or 1)"
)
@click.option(
    "--max-concurrent",
    default=None,
    type=int,
    help="Maximum concurrent downloads (default: from config or 4)"
)
@click.option(
    "--audio-only/--no-audio-only",
    default=None,
    help="Download audio only (default: from config or False)"
)
@click.option(
    "--audio-format",
    default=None,
    type=click.Choice(["mp4", "mp3"]),
    help="Audio format for audio-only downloads (default: from config or 'mp4')"
)
@click.version_option(__version__)
def main(
    url: str,
    output: Optional[str],
    quality: Optional[str],
    prefix_index: Optional[bool],
    retry: Optional[bool],
    retry_attempts: Optional[int],
    max_concurrent: Optional[int],
    audio_only: Optional[bool],
    audio_format: Optional[str]
) -> None:
    """Download YouTube videos or playlists with concurrent and audio-only support."""
    # Load configuration
    config = load_config()

    # Apply defaults from config if not provided via CLI
    output = output or config.get("output", "downloads")
    quality = quality or config.get("quality", "highest")
    prefix_index = prefix_index if prefix_index is not None else config.get("prefix_index", True)
    retry = retry if retry is not None else config.get("retry", False)
    retry_attempts = retry_attempts or config.get("retry_attempts", 1)
    max_concurrent = max_concurrent or config.get("max_concurrent", 4)
    audio_only = audio_only if audio_only is not None else config.get("audio_only", False)
    audio_format = audio_format or config.get("audio_format", "mp4")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Initialize and run downloader
    downloader = YouTubeDownloader(
        output_dir=Path(output),
        quality=quality,
        audio_only=audio_only,
        audio_format=audio_format,
        prefix_index=prefix_index,
        retry=retry,
        retry_attempts=retry_attempts,
        max_concurrent=max_concurrent
    )
    downloader.download(url)

if __name__ == "__main__":
    main()
