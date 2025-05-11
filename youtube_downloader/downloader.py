import logging
from pathlib import Path
from typing import Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor
from pytubefix import YouTube, Playlist
from tqdm import tqdm
from .utils import sanitize_filename, check_ffmpeg, convert_to_mp3

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """Handles downloading YouTube videos and playlists with concurrent and audio-only support."""
    
    def __init__(
        self,
        output_dir: Path,
        quality: str,
        audio_only: bool,
        audio_format: str,
        prefix_index: bool,
        retry: bool,
        retry_attempts: int,
        max_concurrent: int
    ) -> None:
        """Initialize downloader with configuration."""
        self.output_dir = output_dir
        self.quality = quality
        self.audio_only = audio_only
        self.audio_format = audio_format
        self.prefix_index = prefix_index
        self.retry = retry
        self.retry_attempts = retry_attempts
        self.max_concurrent = max_concurrent
    
    def create_output_directory(self, output_path: Path) -> Path:
        """Create output directory if it doesn't exist.
        
        Args:
            output_path: Path to the output directory.
        
        Returns:
            Path: Created directory path.
        """
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
    
    def get_stream(self, yt: YouTube) -> Optional[YouTube.streams]:
        """Get the appropriate video or audio stream.
        
        Args:
            yt: YouTube video object.
        
        Returns:
            Optional stream object or None if no suitable stream is found.
        """
        try:
            if self.audio_only:
                streams = yt.streams.filter(only_audio=True, file_extension="mp4")
                return streams.get_audio_only() or streams.first()
            streams = yt.streams.filter(progressive=True, file_extension="mp4")
            if self.quality == "highest":
                return streams.get_highest_resolution()
            return streams.filter(res=self.quality).first()
        except Exception as e:
            logger.error(f"Error getting stream for {yt.title}: {e}")
            return None
    
    def download_single_video(
        self,
        yt: YouTube,
        output_dir: Path,
        index: Optional[int] = None
    ) -> bool:
        """Download a single YouTube video or audio.
        
        Args:
            yt: YouTube video object.
            output_dir: Directory to save the file.
            index: Optional index for filename prefixing.
        
        Returns:
            bool: True if download succeeded, False otherwise.
        """
        try:
            stream = self.get_stream(yt)
            if not stream:
                logger.error(f"No suitable stream found for {yt.title}")
                return False
            
            ext = "mp3" if self.audio_only and self.audio_format == "mp3" else "mp4"
            filename = sanitize_filename(yt.title) + f".{ext}"
            if index is not None and self.prefix_index:
                filename = f"{index:02d}_{filename}"
            
            logger.info(f"Downloading: {filename}")
            file_size = stream.filesize
            output_path = output_dir / filename
            temp_path = output_dir / f"temp_{filename}" if self.audio_only and self.audio_format == "mp3" else output_path
            
            with tqdm(
                total=file_size,
                unit="B",
                unit_scale=True,
                desc=filename,
                ncols=100
            ) as pbar:
                def on_progress(chunk, file_handler, bytes_remaining):
                    pbar.update(file_size - bytes_remaining - pbar.n)
                
                yt.register_on_progress_callback(on_progress)
                stream.download(output_path=str(temp_path.parent), filename=temp_path.name)
            
            if self.audio_only and self.audio_format == "mp3":
                if not convert_to_mp3(temp_path, output_path):
                    temp_path.rename(output_path.with_suffix(".mp4"))
            
            logger.info(f"Downloaded: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {yt.title}: {e}")
            return False
    
    def download_playlist(self, playlist: Playlist) -> None:
        """Download all videos in a YouTube playlist with concurrent downloads.
        
        Args:
            playlist: YouTube playlist object.
        """
        logger.info(f"Processing playlist: {playlist.title}")
        playlist_folder_name = sanitize_filename(playlist.title)
        playlist_output_dir = self.create_output_directory(self.output_dir / playlist_folder_name)
        total_videos = len(playlist.videos)
        failed_videos: List[Tuple[int, YouTube]] = []
        success_count = 0
        
        def download_task(index: int, video: YouTube) -> Tuple[int, YouTube, bool]:
            """Helper function for concurrent download."""
            result = self.download_single_video(video, playlist_output_dir, index=index)
            return index, video, result
        
        # Initial concurrent download
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            results = list(executor.map(
                lambda x: download_task(x[0], x[1]),
                enumerate(playlist.videos, 1)
            ))
        
        for index, video, success in results:
            if success:
                success_count += 1
            else:
                failed_videos.append((index, video))
        
        # Retry failed downloads
        if self.retry and failed_videos:
            logger.info(f"Retrying {len(failed_videos)} failed downloads...")
            for attempt in range(1, self.retry_attempts + 1):
                logger.info(f"Retry attempt {attempt}/{self.retry_attempts}")
                still_failed = []
                for index, video in failed_videos:
                    logger.info(f"Retrying video {index}/{total_videos}: {video.title}")
                    if self.download_single_video(video, playlist_output_dir, index=index):
                        success_count += 1
                    else:
                        still_failed.append((index, video))
                failed_videos = still_failed
                if not failed_videos:
                    logger.info("All retries successful!")
                    break
        
        # Display summary
        logger.info(f"\nDownload Summary for playlist '{playlist.title}':")
        logger.info(f"Output folder: {playlist_output_dir}")
        logger.info(f"Total videos: {total_videos}")
        logger.info(f"Successfully downloaded: {success_count}")
        if failed_videos:
            logger.info(f"Failed downloads: {len(failed_videos)}")
            for index, video in failed_videos:
                logger.info(f" - Video {index}: {video.title} ({video.watch_url})")
        else:
            logger.info("No failed downloads.")
    
    def download(self, url: str) -> None:
        """Download a YouTube video or playlist.
        
        Args:
            url: YouTube video or playlist URL.
        """
        self.output_dir = self.create_output_directory(self.output_dir)
        try:
            if "playlist" in url.lower():
                playlist = Playlist(url)
                self.download_playlist(playlist)
            else:
                yt = YouTube(url)
                success = self.download_single_video(yt, self.output_dir)
                logger.info("\nDownload Summary:")
                logger.info(f"Output folder: {self.output_dir}")
                logger.info("Total videos: 1")
                logger.info(f"Successfully downloaded: {1 if success else 0}")
                if not success:
                    logger.info(f"Failed: {yt.title} ({yt.watch_url})")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise
