# Multi-stage Docker build for SIYI SDK
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-bad1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    gstreamer1.0-x \
    gstreamer1.0-alsa \
    gstreamer1.0-gl \
    gstreamer1.0-gtk3 \
    gstreamer1.0-qt5 \
    gstreamer1.0-pulseaudio \
    ffmpeg \
    libopencv-dev \
    python3-opencv \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libgstreamer-plugins-bad1.0-0 \
    libgstreamer-plugins-good1.0-0 \
    libgstreamer-plugins-ugly1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml .
COPY requirements.txt* ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt || pip install --no-cache-dir .

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose ports
EXPOSE 37260 8554 1935

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; socket.socket(socket.AF_INET, socket.SOCK_DGRAM).connect(('127.0.0.1', 37260))" || exit 1

# Default command
CMD ["python", "-m", "siyi_sdk.cli", "test", "--ip", "0.0.0.0"]


# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-cov black isort flake8 mypy pre-commit

# Install pre-commit hooks
RUN pre-commit install

# Development command
CMD ["python", "-m", "pytest", "tests/", "-v"]


# Production stage
FROM base as production

# Remove development tools
RUN apt-get update && apt-get remove -y \
    build-essential \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-bad1.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Production command
CMD ["python", "-m", "siyi_sdk.cli", "test", "--ip", "0.0.0.0"]


# Streaming stage with GStreamer
FROM base as streaming

# Install additional streaming dependencies
RUN apt-get update && apt-get install -y \
    gstreamer1.0-plugins-ugly-free \
    gstreamer1.0-plugins-ugly-freeworld \
    && rm -rf /var/lib/apt/lists/*

# Copy streaming configuration
COPY config/streaming.yaml /app/config/

# Streaming command
CMD ["python", "-m", "siyi_sdk.stream", "--config", "/app/config/streaming.yaml"]


# GUI stage with X11 support
FROM base as gui

# Install GUI dependencies
RUN apt-get update && apt-get install -y \
    python3-tk \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Copy GUI configuration
COPY config/gui.yaml /app/config/

# GUI command with virtual display
CMD ["xvfb-run", "python", "-m", "siyi_sdk.gui.tkgui", "--config", "/app/config/gui.yaml"] 