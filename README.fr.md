# VocalLens-AI

Système de transcription et d'analyse de réunions alimenté par l'IA avec une interface d'extension Chrome.

## Fonctionnalités

- Transcription audio en temps réel avec Whisper
- Optimisation pour le français avec CamemBERT
- Fonctionnalité Q&R sur le contenu transcrit
- Performance optimisée pour GPU
- Extension Chrome pour l'enregistrement

## Stack Technique

- **Backend**: FastAPI, Whisper, CamemBERT
- **Stockage**: Base de données vectorielle Qdrant
- **Frontend**: Extension Chrome
- **Infrastructure**: Docker

## Démarrage Rapide

1. **Configuration de l'environnement**
```bash
python -m venv venv
source venv/bin/activate  # ou `venv\Scripts\activate` sous Windows
poetry install
```

2. **Démarrer Qdrant**
```bash
docker-compose up -d
```

3. **Lancer l'API**
```bash
poetry run uvicorn src.api.main:app --reload
```

4. **Installer l'Extension**
- Ouvrir les Extensions Chrome (chrome://extensions/)
- Activer le Mode Développeur
- Charger l'extension non empaquetée depuis `/extension`

## Documentation API

Accédez à la documentation OpenAPI via :
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Prérequis

- Python >=3.10,<3.13
- GPU compatible CUDA (recommandé)
- Navigateur Chrome
- Docker & Docker Compose