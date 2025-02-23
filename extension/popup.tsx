import React, { useState, useRef } from 'react';

const API_URL = 'http://localhost:8000';

const Popup = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [question, setQuestion] = useState('');
  const [answers, setAnswers] = useState([]);
  const mediaRecorder = useRef(null);
  const chunks = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      
      mediaRecorder.current.ondataavailable = (e) => {
        chunks.current.push(e.data);
      };

      mediaRecorder.current.onstop = async () => {
        const blob = new Blob(chunks.current, { type: 'audio/wav' });
        await sendAudio(blob);
        chunks.current = [];
      };

      mediaRecorder.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Error accessing microphone:', err);
    }
  };

  const stopRecording = () => {
    mediaRecorder.current?.stop();
    setIsRecording(false);
  };

  const sendAudio = async (blob: Blob) => {
    const formData = new FormData();
    formData.append('audio', blob);

    try {
      const response = await fetch(`${API_URL}/transcribe`, {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      setTranscript(data.transcript);
    } catch (err) {
      console.error('Error sending audio:', err);
    }
  };

  const sendQuestion = async () => {
    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question })
      });
      
      const data = await response.json();
      setAnswers(data.results);
    } catch (err) {
      console.error('Error sending question:', err);
    }
  };

  return (
    <div className="p-4 w-96">
      <div className="flex flex-col gap-4">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          className={`px-4 py-2 rounded ${
            isRecording ? 'bg-red-500' : 'bg-blue-500'
          } text-white`}
        >
          {isRecording ? 'Stop Recording' : 'Start Recording'}
        </button>

        {transcript && (
          <div className="mt-4">
            <h3 className="font-bold">Transcript:</h3>
            <p className="mt-2">{transcript}</p>
          </div>
        )}

        <div className="mt-4">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question..."
            className="w-full p-2 border rounded"
          />
          <button
            onClick={sendQuestion}
            className="mt-2 px-4 py-2 bg-green-500 text-white rounded"
          >
            Ask
          </button>
        </div>

        {answers.length > 0 && (
          <div className="mt-4">
            <h3 className="font-bold">Answers:</h3>
            {answers.map((answer, i) => (
              <div key={i} className="mt-2 p-2 border rounded">
                <p>{answer.text}</p>
                <p className="text-sm text-gray-500">
                  Score: {Math.round(answer.score * 100)}%
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Popup;