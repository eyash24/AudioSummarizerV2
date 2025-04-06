import streamlit as st
import requests
import tempfile
import os
import json
from moviepy import VideoFileClip
from docx import Document
from fpdf import FPDF 
import yt_dlp

st.set_page_config(page_title="Audio/Video Summarizer", layout="centered", page_icon="📝")

# 🌙 Set Dark Theme Styles
st.markdown("""
    <style>
    .main { background-color: #1E1E1E; color: white; }
    h1, h2, h3, p, label, span, .stButton>button {
        color: white !important;
    }
    .css-ffhzg2 { background-color: #2D2D2D; }
    </style>
""", unsafe_allow_html=True)

st.title("🎧 Audio/Video Summarizer")
st.caption("Upload audio/video or paste a YouTube link to get a transcription or summary.")


# User choice: Upload or YouTube link
option = st.radio("Choose Input Type", ["Upload Audio/Video File", "YouTube Link"], horizontal=True)

uploaded_file = None
youtube_link = None

if option == "Upload Audio/Video File":
    uploaded_file = st.file_uploader("Upload an audio/video file (.mp3, .wav, .mp4)", type=["mp3", "wav", "mp4"])
else:
    youtube_link = st.text_input("Paste YouTube Video Link")

# Toggle for Summary or Full Transcript
mode = st.selectbox("Choose Output Type", ["Summary", "Full Transcription"])

#temp_audio = None
def download_youtube_audio(youtube_link):
    try:
        # Create a temporary file for audio
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, "%(title)s.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'quiet': True,
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_link, download=True)
            filename = ydl.prepare_filename(info).replace(info["ext"], "wav")

        return filename  # This will be path to the .wav file

    except Exception as e:
        st.error(f"❌ Failed to download/process YouTube video.\n\nError: {e}")
        return None
    
# Submit button
if st.button("🔍 Generate"):
    with st.spinner("Processing your input..."):

        temp_audio = None

        # --- 🧠 Preprocessing (Convert Video/YouTube to Audio) ---
        if youtube_link:
            audio_path = download_youtube_audio(youtube_link)
            if audio_path:
                temp_audio = open(audio_path, "rb")
            else:
                temp_audio = None

        elif uploaded_file:
            # If it's mp4, extract audio
            file_ext = uploaded_file.name.split(".")[-1]
            if file_ext == "mp4":
                # Save the uploaded video to a temporary file
                temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp_video.write(uploaded_file.read())
                temp_video.close()  # Close it so moviepy can access it

                try:
                    # Load video with moviepy
                    clip = VideoFileClip(temp_video.name)
                    
                    # Create temporary audio file
                    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                    clip.audio.write_audiofile(temp_audio.name)

                    # ✅ Very important: release resources
                    clip.reader.close()
                    if hasattr(clip.audio, 'reader') and hasattr(clip.audio.reader, 'close_proc'):
                        clip.audio.reader.close_proc()
                    elif hasattr(clip.audio.reader, 'terminate'):
                        clip.audio.reader.terminate()

                    # Optional: You now have the .wav path → temp_audio.name
                    st.success("Video successfully converted to audio.")

                except Exception as e:
                    st.error(f"Error processing video: {e}")
                
                finally:
                    # Clean up video file
                    os.remove(temp_video.name)
            else:
                # Save the uploaded audio file to a temporary file
                temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                temp_audio.write(uploaded_file.read())
                temp_audio.close()
                st.success("Audio file successfully uploaded.")
                
        try:
            # --- 🧠 Transcription/Summarization ---
            if temp_audio.name and os.path.exists(temp_audio.name):
                with open(temp_audio.name, "rb") as f:
                    files = {"file": (os.path.basename(temp_audio.name), f, "multipart/form-data")}
                    response = requests.post("http://localhost:8000/audio-summary/", files=files)
                    response_json = response.json()
                    # print(response_json)
            else:
                st.warning("No audio file was processed. Please check your input and try again.")
                st.stop()

            # Show result based on toggle
            st.subheader("📄 Result")
            result_text = response_json['summary'] if mode == "Summary" else response_json['transcript']
            st.text_area("Output", result_text, height=300)

            # --- 💾 Download Buttons ---
            def download_text():
                with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                    tmp.write(result_text.encode())
                    return tmp.name

            def download_docx():
                doc = Document()
                doc.add_paragraph(result_text)
                path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
                doc.save(path)
                return path

            def download_pdf():
                pdf = FPDF()
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.set_font("Arial", size=12)
                for line in result_text.split('\n'):
                    pdf.multi_cell(0, 10, line)
                path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
                pdf.output(path)
                return path

            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("⬇️ TXT", data=open(download_text(), "rb"), file_name="result.txt")
            with col2:
                st.download_button("⬇️ DOCX", data=open(download_docx(), "rb"), file_name="result.docx")
            with col3:
                st.download_button("⬇️ PDF", data=open(download_pdf(), "rb"), file_name="result.pdf")

        finally:
            if temp_audio:
                try:
                    temp_audio.close()
                except Exception as e:
                    st.warning(f"Failed to close file: {e}")
                
                try:
                    if os.path.exists(temp_audio.name):
                        os.remove(temp_audio.name)
                except Exception as e:
                    st.warning(f"Failed to delete temp audio: {e}")

