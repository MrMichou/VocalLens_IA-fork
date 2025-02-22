# VocalLens-AI

Un système de transcription de réunions et de questions/réponses utilisant Whisper en local avec support du français.

## Fonctionnalités

- Transcription audio locale avec Whisper
- Support natif du français
- Système de Q&A avec embeddings CamemBERT
- Gestion automatique de la mémoire GPU
- Stockage vectoriel avec Qdrant

## Prérequis

- Python 3.8.1 ou supérieur
- Poetry pour la gestion des dépendances
- Docker et Docker Compose pour Qdrant
- GPU recommandé (mais pas obligatoire)
- FFmpeg installé sur le système

## Installation

1. Cloner le dépôt :
```bash
git clone <repo_url>
cd VocalLens-AI
```

2. Installer les dépendances avec Poetry :
```bash
poetry install
```

3. Démarrer Qdrant :
```bash
docker-compose up -d
```

4. Lancer l'application :
```bash
poetry run python app.py
```

## Utilisation

### Transcription
POST `/transcribe`
- Input: Fichier audio (WAV)
- Output: Transcription et métadonnées

### Recherche
POST `/query`
- Input: Question en texte
- Output: Résultats pertinents avec scores

## Configuration

L'application s'adapte automatiquement à votre matériel :
- Sélection automatique du modèle Whisper selon la mémoire GPU
- Optimisation des ressources pour Qdrant
- Gestion intelligente de la mémoire

## Développement

Consultez le CHANGELOG.md pour suivre les évolutions du projet.

## Licence

[Votre licence ici]