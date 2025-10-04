FROM python:3.11-slim-bullseye

# Create a non-root user
RUN groupadd -r botuser && useradd -r -g botuser botuser

# Install system dependencies including ffmpeg
RUN echo "deb http://mirror.yandex.ru/debian bullseye main" > /etc/apt/sources.list && \
    echo "deb http://mirror.yandex.ru/debian-security bullseye-security main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    gnupg \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY src/requirements.txt /app/requirements.txt
COPY ./src/music_bot.py /app/src/music_bot.py

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app/

# Create directory for temporary files and set permissions
RUN mkdir -p /app/temp && \
    chmod -R 755 /app/src && \
    if id "botuser" &>/dev/null 2>&1; then \
        chown -R botuser:botuser /app; \
        echo "Changed ownership to botuser"; \
    fi
# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FFMPEG_PATH=/usr/bin/ffmpeg

RUN chmod +x /app/src/music_bot.py

# Switch to non-root user
USER botuser

# Run bot
CMD ["python", "src/music_bot.py"]
