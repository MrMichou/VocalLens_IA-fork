import { useState, useRef } from 'react';
import { Mic, StopCircle, Send } from "lucide-react";

interface Answer {
  text: string;
  score: number;
}

const PopupComponent = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [question, setQuestion] = useState('');
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [loading, setLoading] = useState(false);
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<BlobPart[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorder.current = recorder;
      audioChunks.current = [];

      recorder.ondataavailable = (event: BlobEvent) => {
        audioChunks.current.push(event.data);
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        await sendAudioToServer(audioBlob);
      };

      recorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
    }
  };

  const sendAudioToServer = async (audioBlob: Blob) => {
    setLoading(true);
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
    } catch (error) {
      console.error('Error sending audio:', error);
    }
    setLoading(false);
  };

  const askQuestion = async () => {
    if (!question.trim()) return;
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:5000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: question }),
      });

      const data = await response.json();
      setAnswers(data.results);
    } catch (error) {
      console.error('Error querying:', error);
    }
    
    setLoading(false);
    setQuestion('');
  };

  return (
    <div className="w-96 h-96 bg-white p-4">
      <div className="flex items-center justify-center space-x-4 mb-4">
        <button 
          className={`px-4 py-2 rounded-md flex items-center ${
            isRecording ? 'bg-red-500 text-white' : 'bg-blue-500 text-white'
          } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={loading}
        >
          {isRecording ? <StopCircle className="w-4 h-4 mr-2" /> : <Mic className="w-4 h-4 mr-2" />}
          {isRecording ? 'Stop Recording' : 'Start Recording'}
        </button>
      </div>

      <div className="flex space-x-2 mb-4">
        <input
          className={`flex-1 px-3 py-2 border rounded-md ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          placeholder="Ask a question about the meeting..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={loading}
        />
        <button 
          className={`px-4 py-2 bg-blue-500 text-white rounded-md flex items-center justify-center ${
            loading || !question.trim() ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-600'
          }`}
          onClick={askQuestion}
          disabled={loading || !question.trim()}
        >
          <Send className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-2 overflow-y-auto max-h-64">
        {answers.map((answer, index) => (
          <div key={index} className="p-3 bg-gray-50 rounded-md shadow-sm">
            <p className="text-sm">{answer.text}</p>
            <p className="text-xs text-gray-500 mt-1">
              Relevance: {(1 - answer.score).toFixed(2)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PopupComponent;