# Simple Dockerfile for running the websocket game server
FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir websockets

EXPOSE 8765
CMD ["python", "main.py"]
