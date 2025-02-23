document.addEventListener('DOMContentLoaded', () => {
    const recordButton = document.getElementById('recordButton');
    const questionInput = document.getElementById('questionInput');
    const askButton = document.getElementById('askButton');
    const answersDiv = document.getElementById('answers');

    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;

    // Recording functionality
    recordButton.addEventListener('click', async () => {
        if (!isRecording) {
            try {
                console.log('Requesting microphone access...');
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: true,
                    video: false
                });
                console.log('Microphone access granted');
                
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = (event) => {
                    console.log('Audio data available');
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    console.log('Recording stopped, preparing to send...');
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    console.log('Audio blob created:', audioBlob.size, 'bytes');
                    await sendAudioToServer(audioBlob);
                };

                mediaRecorder.start(1000); // Collect data every second
                console.log('Recording started');
                isRecording = true;
                recordButton.textContent = 'Stop Recording';
                recordButton.classList.add('recording');
            } catch (error) {
                console.error('Failed to start recording:', error);
                alert('Could not access microphone. Please check permissions.');
            }
        } else {
            console.log('Stopping recording...');
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            isRecording = false;
            recordButton.textContent = 'Start Recording';
            recordButton.classList.remove('recording');
        }
    });

    // Question asking functionality
    askButton.addEventListener('click', async () => {
        const question = questionInput.value.trim();
        if (!question) return;

        try {
            console.log('Sending question:', question);
            askButton.disabled = true;
            questionInput.disabled = true;

            const response = await fetch('http://localhost:5000/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question }),
            });

            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }

            const data = await response.json();
            console.log('Received answer:', data);
            displayAnswers(data.results);
            questionInput.value = '';
        } catch (error) {
            console.error('Failed to get answer:', error);
            alert('Failed to get answer. Please try again.');
        } finally {
            askButton.disabled = false;
            questionInput.disabled = false;
        }
    });

    // Allow Enter key to submit question
    questionInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter' && !askButton.disabled) {
            askButton.click();
        }
    });

    async function sendAudioToServer(audioBlob) {
        console.log('Starting audio transmission...');
        try {
            console.log('Preparing to send audio to server...');
            const formData = new FormData();
            formData.append('audio', audioBlob);
            formData.append('timestamp', new Date().toISOString());

            console.log('Sending audio to server...');
            const response = await fetch('http://localhost:5000/transcribe', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }

            const data = await response.json();
            console.log('Transcription received:', data);
        } catch (error) {
            console.error('Failed to send audio:', error);
            alert('Failed to send audio. Please try again.');
        }
    }

    function displayAnswers(answers) {
        console.log('Displaying answers:', answers);
        if (!Array.isArray(answers)) {
            answersDiv.innerHTML = '<div class="answer">No answers available</div>';
            return;
        }
        
        answersDiv.innerHTML = answers.map(answer => `
            <div class="answer">
                <div>${answer.text}</div>
                <div class="score">Match score: ${(1 - answer.score).toFixed(2)}</div>
            </div>
        `).join('');
    }
});