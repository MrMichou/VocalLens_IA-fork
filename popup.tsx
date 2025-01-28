import React from "react";
import { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import { Button } from "./src/components/ui/button";
import { Input } from "./src/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./src/components/ui/card";

const Popup: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [currentSite, setCurrentSite] = useState<"meet" | "youtube" | null>(null);

  useEffect(() => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const url = tabs[0].url;
      if (url?.includes("meet.google.com")) {
        setCurrentSite("meet");
      } else if (url?.includes("youtube.com")) {
        setCurrentSite("youtube");
      } else {
        setCurrentSite(null);
      }
    });
  }, []);

  const toggleRecording = () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id!, { action: isRecording ? "stopRecording" : "startRecording" });
    });
    setIsRecording(!isRecording);
  };

  const askQuestion = async () => {
    const response = await fetch("http://localhost:5000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await response.json();
    setAnswer(data.answer);
  };

  if (!currentSite) {
    return (
      <Card className="w-[350px]">
        <CardContent>
          <p className="text-center mt-4">Please navigate to Google Meet or YouTube to use this extension.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>AI {currentSite === "meet" ? "Meeting" : "Video"} Assistant</CardTitle>
        <CardDescription>
          Record, transcribe, and ask questions about your {currentSite === "meet" ? "meeting" : "video"}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Button onClick={toggleRecording} className="w-full mb-4">
          {isRecording ? "Stop Recording" : "Start Recording"}
        </Button>
        <Input
          type="text"
          placeholder={`Ask a question about the ${currentSite === "meet" ? "meeting" : "video"}`}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="mb-2"
        />
        <Button onClick={askQuestion} className="w-full">
          Ask
        </Button>
        {answer && (
          <div className="mt-4 p-2 bg-gray-100 rounded">
            <strong>Answer:</strong> {answer}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const root = createRoot(document.getElementById("root")!);
root.render(<Popup />);
