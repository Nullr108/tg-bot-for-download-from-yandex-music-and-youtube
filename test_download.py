import yt_dlp

url = "https://www.youtube.com/watch?v=u8R_oNg0MqM"
output_dir = "temp"
cookies_file = "cookies.txt"
ffmpeg_path = r"C:\Program Files (x86)\ffmpeg-2025-08-25-git-1b62f9d3ae-full_build\bin\ffmpeg.exe"  # Из кода

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': False,
    'extractor_retries': 5,
    'retries': 5,
    'fragment_retries': 5,
    'skip_download_archive': True,
    'no_warnings': False,
    'ffmpeg_location': ffmpeg_path,
    'cookiefile': cookies_file,
    'socket_timeout': 300,
    'noprogress': False,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

print("Download completed!")
