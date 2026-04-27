import streamlit as st
from audiorecorder import audiorecorder # Certifique-se de que é esta a lib
from pydub import AudioSegment
from utils import send_to_backend
import os

st.set_page_config(page_title="Audio AI Transcriber", layout="centered")

st.title("🎙️ Audio Transcriber & AI")
st.write("Grave seu áudio abaixo e processe com inteligência artificial.")

# Pega a pasta onde o app.py REALMENTE está
current_dir = os.path.dirname(os.path.abspath(__file__))
# Sobe um nível se o ffmpeg estiver na raiz e o app na pasta /frontend
root_dir = os.path.dirname(current_dir)

ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg.exe")
ffprobe_path = os.path.join(os.getcwd(), "ffprobe.exe")

AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# 1. Componente de Gravação
audio_bytes = audiorecorder(
    start_prompt="Clique para gravar",
    stop_prompt="Clique para parar",
)

if len(audio_bytes) > 0:
    wav_data = audio_bytes.set_frame_rate(16000).set_channels(1).export(format="wav").read()
    # Reproduz o áudio gravado na tela
    st.audio(wav_data, format="audio/wav")
    
    # 2. Botão de Envio
    if st.button("🚀 Processar Áudio", use_container_width=True):
        with st.spinner("O backend está trabalhando..."):
            result = send_to_backend(wav_data)
            
            if "error" in result:
                st.error(result["error"])
            else:
                # 3. Exibição dos Resultados
                st.divider()
                st.subheader("📝 Transcrição (Vosk)")
                st.info(result["transcription"])
                
                st.subheader("🤖 Análise da IA")
                st.success(result["ai_analysis"])

st.sidebar.markdown("### Status do Sistema")
st.sidebar.write("✅ Frontend: Online")
st.sidebar.write("✅ Backend: Conectado")