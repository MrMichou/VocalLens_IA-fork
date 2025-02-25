let mediaRecorder;
let audioChunks = [];
let processingInterval = null;
const API_URL = 'http://localhost:8000';

// Wait for DOM to fully load
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('recordButton').addEventListener('click', toggleRecording);
  document.getElementById('askButton').addEventListener('click', askQuestion);
  
  // Also enable pressing Enter to submit questions
  document.getElementById('question').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      askQuestion();
    }
  });
});

async function getSupportedMimeType() {
  const mimeTypes = [
    'audio/webm;codecs=opus',
    'audio/ogg;codecs=opus',
    'audio/webm'
  ];
  return mimeTypes.find(type => MediaRecorder.isTypeSupported(type)) || 'audio/webm';
}

async function toggleRecording() {
  const button = document.getElementById('recordButton');
  const textDisplay = document.getElementById('transcriptionText');
  
  if (button.textContent === 'Record') {
    // Start recording
    audioChunks = [];
    textDisplay.textContent = '';
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          sampleSize: 16,
        }
      });
      const mimeType = await getSupportedMimeType();
      mediaRecorder = new MediaRecorder(stream, {
        mimeType,
        audioBitsPerSecond: 128000
      });
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };
      
      mediaRecorder.start(3000);
      button.textContent = 'Stop';
      button.classList.add('recording');
      
      // Process when recording stops
      mediaRecorder.onstop = () => {
        processAndTranscribe();
        // Make sure to clear the interval when stopped
        if (processingInterval) {
          clearInterval(processingInterval);
          processingInterval = null;
        }
      };
      
      // Also periodically process during recording
      if (processingInterval) {
        clearInterval(processingInterval); // Clear existing interval if any
      }
      
      processingInterval = setInterval(() => {
        if (mediaRecorder && mediaRecorder.state === 'recording' && audioChunks.length > 0) {
          processAndTranscribe();
        }
      }, 4000);
      
    } catch (error) {
      console.error('Recording error:', error);
      button.textContent = 'Record';
      button.classList.remove('recording');
      alert('Could not access microphone. Please ensure you have granted microphone permissions.');
    }
  } else {
    // Stop recording
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
    
    // Clear processing interval
    if (processingInterval) {
      clearInterval(processingInterval);
      processingInterval = null;
    }
    
    button.textContent = 'Record';
    button.classList.remove('recording');
  }
}

async function processAndTranscribe() {
  if (audioChunks.length === 0) return;
  
  const textDisplay = document.getElementById('transcriptionText');
  const statusEl = document.createElement('div');
  statusEl.className = 'status-message';
  statusEl.textContent = 'Processing audio...';
  textDisplay.appendChild(statusEl);
  
  try {
    const mimeType = mediaRecorder.mimeType;
    const audioBlob = new Blob(audioChunks, { type: mimeType });
    const formData = new FormData();
    formData.append('audio', audioBlob, `audio_${Date.now()}.webm`);
    
    // Clear chunks after creating blob so we don't reprocess
    audioChunks = [];
    
    const response = await fetch(`${API_URL}/transcribe`, {
      method: 'POST',
      body: formData
    });
    
    // Remove status message
    textDisplay.removeChild(statusEl);
    
    if (response.ok) {
      const result = await response.json();
      if (result.transcript?.trim()) {
        // Append transcript with proper spacing
        if (textDisplay.textContent) {
          textDisplay.textContent += ' ' + result.transcript;
        } else {
          textDisplay.textContent = result.transcript;
        }
        
        // Scroll to bottom
        textDisplay.scrollTop = textDisplay.scrollHeight;
      }
    } else {
      console.error('API error:', await response.text());
    }
  } catch (error) {
    console.error('Transcription error:', error);
    // Remove status message if still there
    if (textDisplay.contains(statusEl)) {
      textDisplay.removeChild(statusEl);
    }
  }
}

async function askQuestion() {
  const questionInput = document.getElementById('question');
  const question = questionInput.value.trim();
  
  if (!question) return;
  
  const answer = document.getElementById('answer');
  answer.textContent = 'Processing...';
  answer.classList.add('processing');
  
  try {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    
    answer.classList.remove('processing');
    
    if (response.ok) {
      const result = await response.json();
      
      // Clear answer area
      answer.textContent = '';
      
      if (result.results && result.results.length > 0) {
        // Format results properly
        result.results.forEach((item, index) => {
          const resultEl = document.createElement('div');
          resultEl.className = 'result-item';
          
          const textEl = document.createElement('div');
          textEl.className = 'result-text';
          textEl.textContent = item.text;
          
          const metaEl = document.createElement('div');
          metaEl.className = 'result-meta';
          metaEl.textContent = `Relevance: ${(item.score * 100).toFixed(1)}%`;
          
          resultEl.appendChild(textEl);
          resultEl.appendChild(metaEl);
          
          if (index > 0) {
            const divider = document.createElement('hr');
            answer.appendChild(divider);
          }
          
          answer.appendChild(resultEl);
        });
      } else {
        answer.textContent = 'No relevant information found.';
      }
      
      // Clear question input
      questionInput.value = '';
    } else {
      answer.textContent = 'Error: ' + await response.text();
    }
  } catch (error) {
    answer.classList.remove('processing');
    answer.textContent = 'Error connecting to server. Please try again.';
    console.error('Query error:', error);
  }
}

// Cleanup function for browser extension events
function cleanup() {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
  }
  
  if (processingInterval) {
    clearInterval(processingInterval);
    processingInterval = null;
  }
}

// Handle extension events
window.addEventListener('beforeunload', cleanup);