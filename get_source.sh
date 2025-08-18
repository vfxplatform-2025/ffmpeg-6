#!/bin/bash
set -e

# 현재 디렉토리에서 버전 파악 (ex: ffmpeg-6.1.1 → 6.1.1)
VER=$(basename "$(pwd)" | sed 's/ffmpeg-//')
cd source

ARCHIVE="ffmpeg-${VER}.tar.gz"
DIR="ffmpeg-${VER}"

# 아카이브 다운로드
if [ ! -f "$ARCHIVE" ]; then
    echo "📦 Downloading $ARCHIVE"
    wget "https://ffmpeg.org/releases/${ARCHIVE}"
else
    echo "✅ Archive already exists: $ARCHIVE"
fi

# 기존 디렉토리 제거 후 재추출
if [ -d "$DIR" ]; then
    echo "⚠️ Removing existing source directory: $DIR"
    rm -rf "$DIR"
fi

echo "📂 Extracting $ARCHIVE"
tar -xzf "$ARCHIVE"
