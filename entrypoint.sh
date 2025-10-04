#!/bin/bash

if [ -f /app/cookies.txt ]; then
  chown botuser:botuser /app/cookies.txt
  chmod 644 /app/cookies.txt
fi

exec "$@"
