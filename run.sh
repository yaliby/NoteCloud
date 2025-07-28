#!/bin/bash

trap 'pkill -f "ngrok http"; sudo docker compose down; exit 0' SIGINT

echo "🔧 מריץ Docker Compose..."
sudo docker compose up -d --build

echo "🌍 מריץ ngrok..."
ngrok http --domain=heron-robust-bull.ngrok-free.app 5000

sudo docker compose down

