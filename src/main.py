import os
from dotenv import dotenv_values
import streamlit as st
from groq import Groq
import tempfile
import requests
import json

# Konfigurasi page
st.set_page_config(
    page_title="MileApp Voicenote Summarizer",
    page_icon="🎙️",
    layout="wide"
)

# Handling environment variables
try:
    secrets = dotenv_values(".env")
    GROQ_API_KEY = secrets["GROQ_API_KEY"]
except:
    secrets = st.secrets
    GROQ_API_KEY = secrets["GROQ_API_KEY"]

# Save API key to environment variable
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Inisialisasi Groq client
client = Groq()

def find_m4a_urls(obj):
    """Recursively search for .m4a URLs in any field of the JSON response"""
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
    """Mengambil URL audio dari MileApp API"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    url = f'https://apiweb.mile.app/api/v3/task/{task_id}'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        data = response.json()
        
        # Recursively search for all .m4a URLs in the response
        audio_urls = find_m4a_urls(data)
        
        if not audio_urls:
            raise ValueError("Tidak ditemukan file audio (.m4a) dalam task ini")
            
        return audio_urls[0]  # Return the first found audio URL
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Gagal mengambil data dari MileApp API: {str(e)}")
    except (KeyError, ValueError) as e:
        raise Exception(f"Error dalam memproses response API: {str(e)}")

def download_audio(url):
    """Download audio dari URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Membuat temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.m4a') as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Gagal mengunduh file audio: {str(e)}")

def transcribe_audio(audio_path):
    """Transkripsi audio menggunakan Groq Whisper"""
    try:
        with open(audio_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(audio_path, file.read()),
                model="whisper-large-v3-turbo",
                language="id",
                response_format="verbose_json"
            )
        os.unlink(audio_path)  # Hapus temporary file
        return transcription.text
    except Exception as e:
        os.unlink(audio_path)  # Pastikan temporary file terhapus meski error
        raise e

def analyze_text(text):
    """Analisis teks menggunakan Groq Llama"""
    if not text or not isinstance(text, str):
        raise ValueError("Input teks tidak valid atau kosong")
        
    messages = [
        {
            "role": "system",
            "content": "Anda adalah asisten yang ahli dalam menganalisis voice note. Berikan analisis yang mencakup hal berikut jika perlu disampaikan: Ringkasan utama, Poin-poin penting, Topik utama yang dibahas, Konteks dan implikasi penting, Rekomendasi atau tindak lanjut (jika relevan)"
        },
        {
            "role": "user",
            "content": f"Analisis voice note berikut ini: {text}"
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
            raise ValueError("Analisis menghasilkan teks kosong")
            
        return analysis
        
    except Exception as e:
        raise Exception(f"Gagal menganalisis teks: {str(e)}")

# Title
st.title("🎙️ MileApp Voice Note Summarizer")
st.write("Masukkan Task ID dan Token untuk menganalisis audio dari MileApp")

# Input fields
task_id = st.text_input("📦 Task ID", help="Masukkan Task ID dari MileApp")
token = st.text_input("🔑 Token", type="password", help="Masukkan token autentikasi MileApp")

if st.button("Analisis Voice Note", disabled=not (task_id and token)):
    if not task_id or not token:
        st.error("Mohon masukkan Task ID dan Token")
    else:
        try:
            # Create tabs
            tab1, tab2 = st.tabs(["📊 Ringkasan", "📝 Transkripsi"])
            
            # Get audio URL
            with st.spinner('Mengambil data dari MileApp...'):
                audio_url = get_audio_url(task_id, token)
            
            # Download audio
            with st.spinner('Mengunduh file audio...'):
                audio_path = download_audio(audio_url)
            
            # Transcribe audio
            with st.spinner('Memproses transkripsi audio...'):
                transcription = transcribe_audio(audio_path)
            
            # Analyze transcription
            with st.spinner('Menganalisis transkripsi...'):
                analysis = analyze_text(transcription)
            
            # Display results in tabs
            with tab1:
                st.markdown("### 📊 Analisis")
                analysis_text = st.text_area("Teks Analisis", analysis, height=300, key="analysis_text")
                if st.button("Salin Analisis", key="copy_analysis"):
                    st.write("Teks analisis berhasil disalin ke clipboard")
                    st.clipboard(analysis_text)
            
            with tab2:
                st.markdown("### 📝 Teks Audio")
                transcript = ""
                for segment in transcription.segments:
                    start_time = segment.start
                    end_time = segment.end
                    text = segment.text
                    transcript += f"[{start_time:.2f}-{end_time:.2f}] {text}\n"
                transcript_text = st.text_area("Teks Transkripsi", transcript, height=300, key="transcript_text")
                if st.button("Salin Transkripsi", key="copy_transcript"):
                    st.write("Teks transkripsi berhasil disalin ke clipboard")
                    st.clipboard(transcript_text)
            
            # Success message
            st.success('Proses selesai!')
            
        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")

# Footer
st.markdown("---")
st.caption("A presentation from Mustibisha Group")
