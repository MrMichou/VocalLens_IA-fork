from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import openai
from langchain import OpenAI, VectorDBQA
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import pinecone
import os

app = Flask(__name__)
CORS(app)

# Load environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))

# Initialize Whisper model
whisper_model = whisper.load_model("base")

# Initialize LangChain components
embeddings = OpenAIEmbeddings()
index_name = "meetingtranscripts"
vectorstore = Pinecone.from_existing_index(index_name, embeddings)
qa = VectorDBQA.from_chain_type(llm=OpenAI(), chain_type="stuff", vectorstore=vectorstore)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    audio_file.save("temp_audio.wav")

    result = whisper_model.transcribe("temp_audio.wav")
    transcription = result["text"]

    # Save transcription to Pinecone
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_text(transcription)
    vectorstore.add_texts(texts)

    os.remove("temp_audio.wav")

    return jsonify({"transcription": transcription})

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question')

    if not question:
        return jsonify({"error": "No question provided"}), 400

    answer = qa.run(question)

    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True)

