import asyncio
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import yt_dlp
import logging

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def __init__(self, ffmpeg_path: str, cookies_path: str = None, max_workers: int = 4):
        self.ffmpeg_path = ffmpeg_path
        self.cookies_path = cookies_path
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.chunk_size = 10 * 1024 * 1024  # 10MB

    async def download(self, url: str, output_dir: Path) -> Path:
        """Download video with chunked parallel download"""
        loop = asyncio.get_event_loop()
        ydl_opts = self._get_base_ydl_opts(output_dir)
        
        # Enable internal chunked download
        ydl_opts.update({
            'http_chunk_size': self.chunk_size,
            'retries': 10,
            'fragment_retries': 10,
            'extractor_retries': 10,
            'socket_timeout': 600,
            'noprogress': False
        })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await loop.run_in_executor(
                    self.executor, 
                    lambda: ydl.extract_info(url, download=True)
                )
                filename = ydl.prepare_filename(info)
                return Path(filename)
        except Exception as e:
            logger.error(f"YouTube download error: {str(e)}")
            raise

    def _get_base_ydl_opts(self, output_dir: Path) -> dict:
        """Base configuration for yt-dlp"""
        return {
            'format': 'bestaudio/best',
            'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'extractor_retries': 5,
            'retries': 5,
            'fragment_retries': 5,
            'skip_download_archive': True,
            'no_warnings': True,
            'ffmpeg_location': self.ffmpeg_path,
            'cookiefile': self.cookies_path if self.cookies_path and os.path.exists(self.cookies_path) else None,
            'socket_timeout': 300,
            'noprogress': False,
            'http_chunk_size': self.chunk_size,
        }
