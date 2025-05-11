import re
from pathlib import Path
import subprocess
import shutil
import logging

logger = logging.getLogger(__name__)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename or folder name by removing invalid characters.

    Args:
        filename: String to sanitize.

    Returns:
        str: Sanitized string.
    """
    return re.sub(r'[<>:"/\\|?*]', '', filename).strip()

def check_ffmpeg() -> bool:
    """Check if ffmpeg is installed.

    Returns:
        bool: True if ffmpeg is available, False otherwise.
    """
    return shutil.which("ffmpeg") is not None

def convert_to_mp3(input_path: Path, output_path: Path) -> bool:
    """Convert MP4 audio to MP3 using ffmpeg.

    Args:
        input_path: Path to input MP4 file.
        output_path: Path to output MP3 file.

    Returns:
        bool: True if conversion succeeded, False otherwise.
    """
    try:
        if not check_ffmpeg():
            logger.warning("ffmpeg not found; keeping MP4 audio.")
            return False
        cmd = [
            "ffmpeg", "-i", str(input_path), "-vn", "-acodec", "mp3",
            "-ab", "192k", "-y", str(output_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        input_path.unlink()  # Remove original MP4
        return True
    except Exception as e:
        logger.error(f"Failed to convert to MP3: {e}")
        return False
