let mediaRecorder;
let audioChunks = [];
const API_URL = 'http://localhost:8000';

document.getElementById('recordButton').addEventListener('click', toggleRecording);
document.getElementById('askButton').addEventListener('click', askQuestion);

async function toggleRecording() {
  const button = document.getElementById('recordButton');
  const textDisplay = document.getElementById('transcriptionText');
  
  if (button.textContent === 'Record') {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm; codecs=opus'
    });
    
    mediaRecorder.ondataavailable = async (event) => {
      const formData = new FormData();
      formData.append('audio', event.data, 'audio.webm');
      
      try {
        const response = await fetch(`${API_URL}/transcribe`, {
          method: 'POST',
          body: formData
        });
        
        const result = await response.json();
        if (result.transcript) {
          textDisplay.textContent += result.transcript + ' ';
        }
      } catch (error) {
        console.error('Error:', error);
      }
    };
    
    mediaRecorder.start(2000);
    button.textContent = 'Stop';
    button.classList.add('recording');
    textDisplay.textContent = '';
  } else {
    mediaRecorder.stop();
    const tracks = mediaRecorder.stream.getTracks();
    tracks.forEach(track => track.stop());
    button.textContent = 'Record';
    button.classList.remove('recording');
  }
}

async function askQuestion() {
  const question = document.getElementById('question').value;
  const answer = document.getElementById('answer');
  
  try {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    
    const result = await response.json();
    answer.textContent = result.results.join('\n');
  } catch (error) {
    console.error('Error:', error);
    answer.textContent = 'Error getting response';
  }
}