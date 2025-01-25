# Use the official Python image as the base
FROM python:3.9-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:99 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    tesseract-ocr \
    libtesseract-dev \
    espeak-ng \
    portaudio19-dev \
    gcc \
    build-essential \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Set working directory
WORKDIR /app

# Copy application code
COPY . /app

# Expose ports (if needed for additional services, e.g., a web server)
EXPOSE 5000

# Start Xvfb and run the DS Assistant
CMD Xvfb :99 -screen 0 1024x768x24 & python ds_assistant.py