# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.1] - 2025-02-23

### Fixed
- Python version compatibility with numpy and qdrant-client (>=3.10,<3.13)
- Configuration settings validation with pydantic-settings
- Environment variables handling

## [0.5.0] - 2025-02-23

### Added
- Migration vers FastAPI
- Support asynchrone pour une meilleure performance
- Documentation API automatique (Swagger/ReDoc)
- Validation des données avec Pydantic
- Tests automatisés avec pytest-asyncio

### Changed
- Restructuration complète du projet
- Amélioration de la gestion des erreurs
- Optimisation de la gestion mémoire GPU
- Interface extension Chrome mise à jour
- Documentation mise à jour

## [0.4.0] - 2025-02-22

### Added
- French language support with CamemBERT embeddings
- Automatic model selection based on available GPU memory
- Memory management features for GPU optimization
- Language detection metadata in transcription results

### Changed
- Switched to CamemBERT for better French language understanding
- Implemented dynamic Whisper model selection (base/medium)
- Improved GPU memory handling with automatic cleanup
- Enhanced error handling and logging

### Technical Details
- Added memory check before loading Whisper models
- Integrated garbage collection for better memory management
- Updated vector dimensions for CamemBERT compatibility
- Added model type tracking in metadata

## [0.3.0] - 2025-02-22

### Added
- Local Whisper integration replacing OpenAI API
- GPU support for Whisper transcription
- Temporary file handling for audio processing

### Changed
- Switched from OpenAI API to local Whisper model
- Updated Poetry dependencies
- Improved error handling and logging

### Dependencies
- Added openai-whisper
- Added torch
- Added numpy
- Removed openai package

## [0.2.0] - 2025-02-22

### Added
- Basic Chrome extension frontend implementation
- Audio recording functionality in extension
- Question/Answer interface in extension
- Real-time communication with backend

### Changed
- Simplified backend removing Qdrant temporarily
- Updated microphone permissions to use audioCapture
- Improved error handling and logging

## [0.1.0] - 2025-02-21

### Changed
- Replaced Pinecone with Qdrant as vector database
- Migrated to Poetry for dependency management
- Updated Python version constraint to `>=3.8.1,<3.12`

### Added
- Docker Compose setup for Qdrant
- Poetry configuration (pyproject.toml)
- This CHANGELOG file