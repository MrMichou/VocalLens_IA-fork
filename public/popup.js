document.addEventListener('DOMContentLoaded', function() {
    const recordButton = document.getElementById('recordButton');
    const questionInput = document.getElementById('questionInput');
    const askButton = document.getElementById('askButton');
    const answersDiv = document.getElementById('answers');

    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;

    recordButton.addEventListener('click', async () => {
        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    sendAudioToServer(audioBlob);
                };

                mediaRecorder.start();
                isRecording = true;
                recordButton.textContent = 'Stop Recording';
                recordButton.classList.add('recording');
            } catch (err) {
                console.error('Error accessing microphone:', err);
            }
        } else {
            mediaRecorder.stop();
            isRecording = false;
            recordButton.textContent = 'Start Recording';
            recordButton.classList.remove('recording');
        }
    });

    askButton.addEventListener('click', async () => {
        const question = questionInput.value.trim();
        if (!question) return;

        askButton.disabled = true;
        try {
            const response = await fetch('http://localhost:5000/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question }),
            });

            const data = await response.json();
            displayAnswers(data.results);
            questionInput.value = '';
        } catch (err) {
            console.error('Error asking question:', err);
        }
        askButton.disabled = false;
    });

    async function sendAudioToServer(audioBlob) {
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob);
            formData.append('timestamp', new Date().toISOString());

            const response = await fetch('http://localhost:5000/transcribe', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            console.log('Transcription:', data.transcript);
        } catch (err) {
            console.error('Error sending audio:', err);
        }
    }

    function displayAnswers(answers) {
        answersDiv.innerHTML = answers.map(answer => `
            <div class="answer">
                <p>${answer.text}</p>
                <small>Relevance: ${(1 - answer.score).toFixed(2)}</small>
            </div>
        `).join('');
    }
});