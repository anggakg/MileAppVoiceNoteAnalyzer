import os
from dotenv import load_dotenv
import streamlit as st
from groq import Groq
import tempfile
import requests
import json
import pyperclip

# Configure Streamlit page
st.set_page_config(
    page_title="MileApp Voicenote Summarizer",
    page_icon="🎙️",
    layout="wide"
)

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY is not set. Please ensure it's available in the `.env` file or environment variables.")
    st.stop()

# Initialize Groq client
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"Failed to initialize Groq client: {str(e)}")
    st.stop()

# Utility functions
def find_m4a_urls(obj):
    """Recursively search for .m4a URLs in any field of the JSON response."""
    urls = []

    def recursive_search(item):
        if isinstance(item, dict):
            for value in item.values():
                recursive_search(value)
        elif isinstance(item, list):
            for element in item:
                recursive_search(element)
        elif isinstance(item, str) and item.lower().endswith('.m4a'):
            urls.append(item)

    recursive_search(obj)
    return urls

def get_audio_url(task_id, token):
    """Retrieve audio URL from MileApp API."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    url = f'https://apiweb.mile.app/api/v3/task/{task_id}'

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Search for .m4a URLs
        audio_urls = find_m4a_urls(data)
        if not audio_urls:
            raise ValueError("No .m4a audio file found in this task.")
        return audio_urls[0]
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch data from MileApp API: {str(e)}")
    except (KeyError, ValueError) as e:
        raise Exception(f"Error processing API response: {str(e)}")

def download_audio(url):
    """Download audio file from URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.m4a') as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download audio file: {str(e)}")

def transcribe_audio(audio_path):
    """Transcribe audio using Groq Whisper."""
    try:
        with open(audio_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(audio_path, file.read()),
                model="whisper-large-v3-turbo",
                language="id",
                response_format="verbose_json"
            )
        os.unlink(audio_path)  # Remove temporary file
        return transcription.text
    except Exception as e:
        os.unlink(audio_path)  # Ensure file is deleted on error
        raise Exception(f"Failed to transcribe audio: {str(e)}")

def analyze_text(text):
    """Analyze text using Groq Llama."""
    if not text or not isinstance(text, str):
        raise ValueError("Invalid or empty input text.")

    messages = [
        {
            "role": "system",
            "content": "You are an expert assistant analyzing voice notes. Provide insights such as key summaries, main points, and actionable recommendations if relevant."
        },
        {
            "role": "user",
            "content": f"Analyze the following voice note: {text}"
        }
    ]

    analysis = ""
    try:
        stream = client.chat.completions.create(
            model="llama-3.2-90b-text-preview",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                analysis += chunk.choices[0].delta.content

        if not analysis.strip():
            raise ValueError("Analysis resulted in empty text.")
        return analysis
    except Exception as e:
        raise Exception(f"Failed to analyze text: {str(e)}")

# Main Streamlit UI
st.title("🎙️ MileApp Voice Note Summarizer")
st.write("Enter Task ID and Token to analyze audio from MileApp.")

# Input fields
task_id = st.text_input("📦 Task ID", help="Enter the Task ID from MileApp")
token = st.text_input("🔑 Token", type="password", help="Enter the MileApp authentication token")

if st.button("Analyze Voice Note"):
    if not task_id or not token:
        st.error("Please provide both Task ID and Token.")
    else:
        try:
            # Create tabs
            tab1, tab2 = st.tabs(["📊 Summary", "📝 Transcription"])

            with st.spinner('Fetching data from MileApp...'):
                audio_url = get_audio_url(task_id, token)

            with st.spinner('Downloading audio file...'):
                audio_path = download_audio(audio_url)

            with st.spinner('Processing audio transcription...'):
                transcription = transcribe_audio(audio_path)

            with st.spinner('Analyzing transcription...'):
                analysis = analyze_text(transcription)

            # Display results in tabs
            with tab1:
                st.markdown("### 📊 Analysis")
                st.code(analysis, language="markdown")
                if st.button("Copy Analysis", key="copy_analysis"):
                    pyperclip.copy(analysis)
                    st.success("Analysis text copied to clipboard.")

            with tab2:
                st.markdown("### 📝 Transcription")
                st.text_area("Transcribed Text", transcription, height=300, key="transcript_text", disabled=True)
                if st.button("Copy Transcription", key="copy_transcription"):
                    pyperclip.copy(transcription)
                    st.success("Transcription text copied to clipboard.")

            st.success('Process completed!')

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.caption("A presentation from Mustibisha Group")
