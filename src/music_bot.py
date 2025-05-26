import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
import re
import asyncio
import shutil

import yt_dlp
from yandex_music import Client
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
YANDEX_TOKEN = os.getenv("YANDEX_TOKEN")

# Determine ffmpeg path based on platform
def get_ffmpeg_path():
    # Check if path is set in environment variables
    if ffmpeg_env := os.getenv("FFMPEG_PATH"):
        return ffmpeg_env
    
    # For Linux, try to find ffmpeg in PATH
    if os.name != 'nt':
        if ffmpeg_path := shutil.which('ffmpeg'):
            return ffmpeg_path
        
    # Default Windows path
    return r"C:\Program Files (x86)\ffmpeg-2025-04-23-git-25b0a8e295-full_build\bin\ffmpeg.exe"

FFMPEG_PATH = get_ffmpeg_path()

# Verify ffmpeg is available
if not Path(FFMPEG_PATH).exists() and not shutil.which('ffmpeg'):
    print("⚠️ Warning: FFmpeg not found. Please install FFmpeg or set correct FFMPEG_PATH")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file")

# Initialize Yandex Music client only if token is available
yandex_client = None
if YANDEX_TOKEN:
    try:
        yandex_client = Client(YANDEX_TOKEN).init()
        print("✅ Yandex Music client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Yandex Music client: {str(e)}")

# Setup directories
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)
COOKIES_FILE = Path("cookies.txt")  # Path to the cookies file

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def download_youtube_audio(url: str, output_dir: Path) -> Path:
    """Downloads audio from YouTube and returns the file path"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'extractor_retries': 3,
        'fragment_retries': 3,
        'skip_download_archive': True,
        'no_warnings': True,
        'ffmpeg_location': FFMPEG_PATH
    }

    if COOKIES_FILE.exists():
        ydl_opts['cookiefile'] = str(COOKIES_FILE)
        print(f"Using cookies file: {COOKIES_FILE}")

    try:
        # Run YouTube-DL in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            return Path(filename)
    except Exception as e:
        print(f"YouTube download error: {str(e)}")
        raise Exception(f"Failed to download audio: {str(e)}")

async def download_yandex_track(track_id: str, album_id: str, output_dir: Path) -> Path:
    """Downloads audio from Yandex Music and returns the file path"""
    if not yandex_client:
        raise ValueError("Yandex Music client is not initialized")
        
    track = yandex_client.tracks([f"{track_id}:{album_id}"])[0]
    filename = f"{track.artists[0].name} - {track.title}.mp3"
    filepath = output_dir / filename
    
    track.download(filepath)
    return filepath

def extract_yandex_ids(url: str) -> tuple:
    """Extracts track and album IDs from Yandex Music URL"""
    pattern = r"album/(\d+)/track/(\d+)"
    match = re.search(pattern, url)
    if match:
        album_id, track_id = match.groups()
        return track_id, album_id
    return None, None

@dp.message(Command("start"))
async def start(message: types.Message):
    response = "Привет! Я могу скачивать аудио из:"
    response += "\n- YouTube"
    if yandex_client:
        response += "\n- Яндекс.Музыки"
    response += "\n\nПросто отправь мне ссылку!"
    await message.answer(response)

@dp.message(F.text.contains("music.yandex.ru"))
async def handle_yandex_url(message: types.Message):
    if not yandex_client:
        await message.reply("❌ Извините, поддержка Яндекс.Музыки временно недоступна")
        return
        
    url = message.text.strip()
    user_dir = TEMP_DIR / str(message.from_user.id)
    user_dir.mkdir(exist_ok=True)
    
    try:
        msg = await message.reply("⏳ Начинаю загрузку трека с Яндекс.Музыки...")
        track_id, album_id = extract_yandex_ids(url)
        
        if not track_id or not album_id:
            await message.reply("❌ Неверный формат ссылки на Яндекс.Музыку")
            return
            
        audio_path = await download_yandex_track(track_id, album_id, user_dir)
        
        await msg.edit_text("✅ Аудио готово! Отправляю...")
        audio = FSInputFile(audio_path, filename=audio_path.name)
        await message.reply_audio(audio)
        await msg.delete()
        
    except Exception as e:
        await message.reply(f"❌ Ошибка: {str(e)}")
    finally:
        # Cleanup temporary files
        for file in user_dir.glob("*.*"):
            try:
                file.unlink()
            except:
                pass

@dp.message(F.text.contains("youtube.com") | F.text.contains("youtu.be"))
async def handle_youtube_url(message: types.Message):
    url = message.text.strip()
    user_dir = TEMP_DIR / str(message.from_user.id)
    user_dir.mkdir(exist_ok=True)
    
    try:
        msg = await message.reply("⏳ Начинаю загрузку с YouTube...")
        audio_path = await download_youtube_audio(url, user_dir)  # Note the await here
        
        await msg.edit_text("✅ Аудио готово! Отправляю...")
        audio = FSInputFile(audio_path, filename=audio_path.name)
        await message.reply_audio(audio)
        await msg.delete()
        
    except Exception as e:
        await message.reply(f"❌ Ошибка: {str(e)}")
    finally:
        # Cleanup temporary files
        for file in user_dir.glob("*.*"):
            try:
                file.unlink()
            except:
                pass

if __name__ == "__main__":
    dp.run_polling(bot)