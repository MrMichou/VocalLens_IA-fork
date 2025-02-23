let mediaRecorder = null;
let audioChunks = [];

document.getElementById('recordButton').addEventListener('click', toggleRecording);
document.getElementById('askButton').addEventListener('click', askQuestion);

async function toggleRecording() {
  const button = document.getElementById('recordButton');
  
  if (!mediaRecorder) {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      await sendAudio(audioBlob);
      audioChunks = [];
    };

    mediaRecorder.start();
    button.textContent = 'Stop Recording';
    button.classList.add('recording');
  } else {
    mediaRecorder.stop();
    mediaRecorder = null;
    button.textContent = 'Start Recording';
    button.classList.remove('recording');
  }
}

async function sendAudio(blob) {
  const formData = new FormData();
  formData.append('audio', blob);

  try {
    const response = await fetch('http://localhost:8000/transcribe', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    document.getElementById('transcript').textContent = data.transcript;
  } catch (error) {
    console.error('Error:', error);
  }
}

async function askQuestion() {
  const question = document.getElementById('question').value;
  if (!question) return;

  try {
    const response = await fetch('http://localhost:8000/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    
    const data = await response.json();
    const answersDiv = document.getElementById('answers');
    answersDiv.innerHTML = data.results
      .map(result => `<p>${result.text} (Score: ${Math.round(result.score * 100)}%)</p>`)
      .join('');
  } catch (error) {
    console.error('Error:', error);
  }
}