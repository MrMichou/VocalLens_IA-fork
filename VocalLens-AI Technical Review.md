# VocalLens-AI Technical Stack Review

## Frontend Setup (Chrome Extension)
### Requirements
- Chrome Browser
- Extension Developer Mode enabled

### Key Technologies
- Vanilla JavaScript
- Chrome Extension APIs
- MediaRecorder API for audio capture

### Extension Structure
```
extension/
├── manifest.json    # Extension configuration
├── popup.html      # Simple UI interface
└── popup.js        # Audio capture and API logic
```

## Backend Setup
### Requirements
- Python 3.8+
- OpenAI API key
- CUDA-capable GPU (recommended for Whisper)

### Key Technologies
- Flask + CORS
- OpenAI Whisper
- Future: LangChain + Qdrant

## Development Environment
```bash
# Backend Setup
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Frontend Setup (Chrome Extension)
1. Open Chrome
2. Go to chrome://extensions/
3. Enable Developer Mode
4. Load unpacked extension from /extension folder
```

## Environment Variables
```env
OPENAI_API_KEY=your_openai_key
```

## Potential Technical Challenges
1. **Audio Processing**
   - Whisper requires significant computational resources
   - Consider cloud GPU options for production
   - Audio format compatibility between browsers

2. **Extension Performance**
   - Audio capture might impact browser performance
   - Network latency for audio transmission
   - Browser memory management for long recordings

3. **API Rate Limits**
   - OpenAI has request/minute limitations
   - Implement rate limiting and error handling

## Production Considerations
- Implement proper error handling
- Add request validation
- Setup monitoring for API usage
- Consider audio compression
- Implement proper audio file cleanup
- Add user authentication
- Setup HTTPS for production endpoints
- Consider WebRTC for better audio streaming