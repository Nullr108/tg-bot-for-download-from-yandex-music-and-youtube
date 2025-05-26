# Music Bot Application

This project is a Python-based music bot that allows users to download audio from YouTube and Yandex Music. The bot is built using the `aiogram` library for handling Telegram bot interactions and `yt-dlp` for downloading audio tracks.

## Project Structure

```
music-bot
├── src
│   ├── music_bot.py        # Main code for the music bot application
│   └── requirements.txt     # Python dependencies
├── .env                     # Environment variables
├── .dockerignore            # Files to ignore when building the Docker image
├── docker-compose.yml       # Docker services configuration
├── Dockerfile               # Instructions for building the Docker image
└── README.md                # Project documentation
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed on your machine.
- A Telegram bot token from [BotFather](https://core.telegram.org/bots#botfather).
- A Yandex Music API token.

### Obtaining Yandex Music Token

There are several official ways to obtain your Yandex Music token:

1. Using the Web App (works for most accounts):
   - Visit [music-yandex-bot.ru](https://music-yandex-bot.ru)
   - Follow the authentication process
   - Copy the provided token

2. Using Android App (works for all accounts):
   - Download the APK from [Releases Page](https://github.com/MarshalX/yandex-music-token/releases)
   - Install and run the app
   - Follow the authentication process
   - Copy the provided token

3. Using Browser Extension (OAuth method):
   - Install the extension for [Chrome](https://chrome.google.com/webstore/detail/yandex-music-token/lcbjeookjibfhjjopieifgjnhlegmkib) or [Firefox](https://addons.mozilla.org/en-US/firefox/addon/yandex-music-token/)
   - Follow the extension's instructions
   - Copy the token from the extension

### Environment Variables

Create a `.env` file in the root directory of the project with the following content:

```
BOT_TOKEN=your_telegram_bot_token
YANDEX_TOKEN=your_yandex_music_api_token
```

### Cookies Configuration

To download content from YouTube and Yandex Music that requires authentication, you'll need to provide cookies. Create a `cookies.txt` file in the root directory with your browser cookies:

1. Install the "Get cookies.txt" extension for your browser:
   - [Chrome/Edge Extension](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid)
   - [Firefox Extension](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. Visit YouTube and/or Yandex Music while logged in
3. Use the extension to export cookies for these domains
4. Save the exported cookies as `cookies.txt` in the project root directory

The Docker setup will automatically use these cookies for authentication.

### Building the Docker Image

To build the Docker image, run the following command in the root directory of the project:

```bash
docker build -t music-bot .
```

### Running the Application

To run the music bot application using Docker Compose, execute the following command:

```bash
docker-compose up
```

This will start the bot and make it available for use.

### Usage

Once the bot is running, you can interact with it on Telegram by sending links to YouTube or Yandex Music tracks. The bot will download the audio and send it back to you.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.