import io

import requests
import streamlit as st
from audiorecorder import audiorecorder

from app.components.report_form import render as render_report
from app.state.session import (
    clear_report,
    get_recorded_audio,
    get_relator,
    get_report,
    get_transcript,
    set_recorded_audio,
    set_relator,
    set_report,
    set_transcript,
)

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Relato de Problema TI", layout="centered")
st.title("Relato de Problema — TI")


def _transcribe(audio_bytes: bytes, filename: str, mime: str = "audio/wav") -> bool:
    if not get_relator().strip():
        st.warning("Informe seu nome na barra lateral antes de continuar.")
        return False
    with st.spinner("Transcrevendo..."):
        resp = requests.post(
            f"{API_URL}/process-audio",
            files={"file": (filename, audio_bytes, mime)},
        )
    if resp.status_code == 200:
        st.session_state.pop("report", None)
        set_transcript(resp.json().get("transcription", ""))
        st.rerun()
    else:
        st.error(f"Erro: {resp.json().get('detail', resp.status_code)}")
    return False


def _structure(text: str, relator: str):
    if not relator.strip():
        st.warning("Informe seu nome na barra lateral antes de continuar.")
        return
    if not text.strip():
        st.warning("Nenhum texto para estruturar.")
        return
    with st.spinner("Estruturando relato via IA..."):
        resp = requests.post(
            f"{API_URL}/structure-report",
            json={"text": text, "relator": relator},
        )
    if resp.status_code == 200:
        set_report(resp.json())
        st.rerun()
    else:
        st.error(f"Erro: {resp.json().get('detail', resp.status_code)}")


# --- Sidebar ---
with st.sidebar:
    st.header("Identificação")
    relator = st.text_input("Seu nome", value=get_relator())
    if relator != get_relator():
        set_relator(relator)

    st.divider()
    try:
        resp = requests.get(f"{API_URL}/health", timeout=2)
        info = resp.json()
        st.success("Backend online")
        st.caption(
            f"Vosk: {'✓' if info.get('model_ready') else '✗'}  |  "
            f"IA: {'✓' if info.get('ai_available') else '✗'}"
        )
    except Exception:
        st.error("Backend offline — rode scripts/run_dev.sh")


# --- Resultado (se já tiver relato estruturado) ---
report = get_report()
if report:
    updated = render_report(report)
    st.divider()
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Confirmar e Salvar", type="primary"):
            updated["status"] = "Corrigido"
            set_report(updated)
            st.success(f"Salvo em: {report.get('file', 'data/reports/')}")
    with col2:
        if st.button("Novo relato"):
            clear_report()
            st.rerun()
    st.stop()


# --- Transcrição (se já tiver texto, mostra antes das abas) ---
transcript = get_transcript()
if transcript:
    st.subheader("Transcrição")
    edited = st.text_area("Revise o texto antes de estruturar", value=transcript, height=150)
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Estruturar Relato", type="primary", key="btn_structure"):
            _structure(edited, relator)
    with col2:
        if st.button("Regravar / Novo", key="btn_reset"):
            set_transcript("")
            st.rerun()
    st.stop()


# --- Entrada ---
tab_gravar, tab_upload, tab_texto = st.tabs(["Gravar", "Upload", "Texto"])

with tab_gravar:
    st.caption("Clique para gravar, clique novamente para parar.")
    audio = audiorecorder(
        start_prompt="Iniciar gravação",
        stop_prompt="Parar gravação",
        pause_prompt="",
        key="recorder",
    )

    # Salva o áudio no session_state assim que chegar — evita perda no rerun
    if len(audio) > 0:
        buf = io.BytesIO()
        audio.export(buf, format="wav")
        set_recorded_audio(buf.getvalue())

    wav_bytes = get_recorded_audio()
    if wav_bytes:
        st.audio(wav_bytes, format="audio/wav")
        if st.button("Transcrever", key="btn_transcribe_rec", type="primary"):
            _transcribe(wav_bytes, "gravacao.wav", "audio/wav")

with tab_upload:
    uploaded = st.file_uploader(
        "Envie um arquivo de áudio",
        type=["wav", "mp3", "ogg", "flac", "m4a", "mp4", "webm"],
    )
    if uploaded:
        if st.button("Transcrever", key="btn_transcribe_upload", type="primary"):
            _transcribe(uploaded.getvalue(), uploaded.name, uploaded.type)

with tab_texto:
    texto = st.text_area("Descreva o problema livremente", height=180, key="texto_livre")
    if st.button("Estruturar Relato", key="btn_structure_text", type="primary"):
        _structure(texto, relator)
