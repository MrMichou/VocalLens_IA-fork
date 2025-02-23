# VocalLens-AI: Meeting Transcription & QA System

## Architecture

### Chrome Extension (Frontend)
- `extension/popup.html` - Interface utilisateur simple
- `extension/popup.js` - Logique JavaScript pour l'enregistrement et les requêtes
- `extension/manifest.json` - Configuration de l'extension

### Flask Backend (`app.py`)
- Audio transcription endpoint
- Question-answering endpoint
- Simple in-memory storage (temporaire)

## Core Features
1. **Audio Transcription**
   - Uses OpenAI Whisper for speech-to-text
   - Captures audio via Chrome extension

2. **Question-Answering**
   - Simple text search (actuel)
   - Prévu : intégration avec LangChain + Qdrant

## Data Flow
1. Chrome extension captures audio using MediaRecorder API
2. Audio envoyé au backend via FormData
3. Backend transcrit avec Whisper
4. Les utilisateurs peuvent poser des questions via l'interface
5. Le backend recherche et renvoie les réponses pertinentes

## Dependencies
- Frontend: Vanilla JavaScript, Chrome Extension APIs
- Backend: Flask, Whisper, OpenAI API
- Future: LangChain, Qdrant

## Security Notes
- Requires OpenAI API key
- CORS enabled for extension-backend communication
- Requires audioCapture permission in Chrome
- Temporary audio file handling