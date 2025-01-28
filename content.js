let mediaRecorder
const audioChunks = []
let audioContext
let source

function startRecording() {
  if (window.location.hostname === "meet.google.com") {
    startMeetRecording()
  } else if (window.location.hostname === "www.youtube.com") {
    startYouTubeRecording()
  }
}

function startMeetRecording() {
  navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
    mediaRecorder = new MediaRecorder(stream)
    mediaRecorder.start()

    mediaRecorder.addEventListener("dataavailable", (event) => {
      audioChunks.push(event.data)
    })

    mediaRecorder.addEventListener("stop", () => {
      const audioBlob = new Blob(audioChunks)
      sendAudioToServer(audioBlob)
    })
  })
}

function startYouTubeRecording() {
  const video = document.querySelector("video")
  if (!video) {
    console.error("No video element found")
    return
  }

  audioContext = new (window.AudioContext || window.webkitAudioContext)()
  source = audioContext.createMediaElementSource(video)
  const destination = audioContext.createMediaStreamDestination()
  source.connect(destination)
  source.connect(audioContext.destination)

  mediaRecorder = new MediaRecorder(destination.stream)
  mediaRecorder.start()

  mediaRecorder.addEventListener("dataavailable", (event) => {
    audioChunks.push(event.data)
  })

  mediaRecorder.addEventListener("stop", () => {
    const audioBlob = new Blob(audioChunks)
    sendAudioToServer(audioBlob)
  })
}

function sendAudioToServer(audioBlob) {
  const formData = new FormData()
  formData.append("audio", audioBlob, "recording.wav")

  fetch("http://localhost:5000/transcribe", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Transcription:", data.transcription)
    })
    .catch((error) => {
      console.error("Error:", error)
    })
}

