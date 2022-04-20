# Build an intermediate image for the Python requirements
FROM python:3.9-slim-buster as intermediate

# Install Python requirements
COPY requirements.txt .
RUN python -m pip install --no-use-pep517 --user -r requirements.txt pip

# Start from a fresh image
FROM python:3.9-slim-buster

RUN apt update && \
    apt install -y \
    iproute2 \
    ffmpeg \
    pulseaudio \
    pulseaudio-utils \
    vlc

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN useradd -u 1000 -d /app appuser
WORKDIR /app

# Copy over the Python requirements from the intermediate container
COPY --from=intermediate /root/.local /app/.local
RUN chown -R appuser: /app

USER appuser

# Get environment variable for the preferred Sonos device
ENV SONOS_DEVICE_IP="${SONOS_DEVICE_IP}"

# Set the main execution command
ENTRYPOINT /app/sonos.py -d "${SONOS_DEVICE_IP}"

# Copy in the code
COPY sonos.py .
