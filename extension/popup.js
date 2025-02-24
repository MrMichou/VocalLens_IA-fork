let mediaRecorder;
let audioChunks = [];
const API_URL = 'http://localhost:8000';

document.getElementById('recordButton').addEventListener('click', toggleRecording);
document.getElementById('askButton').addEventListener('click', askQuestion);

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
      
      mediaRecorder.onstop = processAndTranscribe;
      setInterval(() => {
        if (mediaRecorder.state === 'recording' && audioChunks.length > 0) {
          processAndTranscribe();
        }
      }, 4000);
      
    } catch (error) {
      console.error('Error:', error);
    }
  } else {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
    button.textContent = 'Record';
    button.classList.remove('recording');
  }
}

async function processAndTranscribe() {
  if (audioChunks.length === 0) return;
  
  const textDisplay = document.getElementById('transcriptionText');
  const mimeType = mediaRecorder.mimeType;
  const audioBlob = new Blob(audioChunks, { type: mimeType });
  const formData = new FormData();
  formData.append('audio', audioBlob, 'audio.webm');
  audioChunks = [];
  
  try {
    const response = await fetch(`${API_URL}/transcribe`, {
      method: 'POST',
      body: formData
    });
    
    if (response.ok) {
      const result = await response.json();
      if (result.transcript?.trim()) {
        textDisplay.textContent += result.transcript + ' ';
        textDisplay.scrollTop = textDisplay.scrollHeight;
      }
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

async function askQuestion() {
  const question = document.getElementById('question').value;
  if (!question.trim()) return;
  
  const answer = document.getElementById('answer');
  answer.textContent = 'Processing...';
  
  try {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    
    if (response.ok) {
      const result = await response.json();
      answer.textContent = result.results.join('\n');
    } else {
      answer.textContent = 'Error: ' + await response.text();
    }
  } catch (error) {
    answer.textContent = 'Error getting response';
  }
}