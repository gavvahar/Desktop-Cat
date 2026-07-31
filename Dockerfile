FROM python:3.12-slim

# Qt (xcb platform plugin) + PySide6 runtime libraries, plus build tools for
# pynput's evdev extension (needs linux/input.h, not present in the slim
# base image). No display server is bundled -- the container talks to the
# host's X11 server (see README).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    linux-libc-dev \
    libgl1 \
    libegl1 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libfontconfig1 \
    libfreetype6 \
    libx11-xcb1 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-shm0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxi6 \
    libxrender1 \
    libxext6 \
    libsm6 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/Python \
    QT_QPA_PLATFORM=xcb

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Python/ Python/

CMD ["python", "-m", "desktopcat.main"]
