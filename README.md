# VocalLens-AI

AI-powered meeting transcription and analysis system with a Chrome extension interface.

## Features

- Real-time audio transcription using Whisper
- French language optimization with CamemBERT
- Q&A functionality on transcribed content
- GPU-optimized performance
- Chrome extension for easy recording

## Tech Stack

- **Backend**: FastAPI, Whisper, CamemBERT
- **Storage**: Qdrant vector database
- **Frontend**: Chrome Extension
- **Infrastructure**: Docker

## Quick Start

1. **Environment Setup**
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
poetry install
```

2. **Start Qdrant**
```bash
docker-compose up -d
```

3. **Launch API**
```bash
poetry run uvicorn src.api.main:app --reload
```

4. **Install Extension**
- Open Chrome Extensions (chrome://extensions/)
- Enable Developer Mode
- Load unpacked extension from `/extension`

## API Documentation

Access OpenAPI documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Requirements

- Python >=3.10,<3.13
- CUDA-capable GPU (recommended)
- Chrome Browser
- Docker & Docker Compose