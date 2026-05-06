import streamlit as st


def get_relator() -> str:
    return st.session_state.get("relator", "")

def set_relator(v: str):
    st.session_state["relator"] = v

def get_transcript() -> str:
    return st.session_state.get("transcript", "")

def set_transcript(v: str):
    st.session_state["transcript"] = v

def get_report() -> dict | None:
    return st.session_state.get("report")

def set_report(v: dict):
    st.session_state["report"] = v

def get_recorded_audio() -> bytes | None:
    return st.session_state.get("recorded_audio")

def set_recorded_audio(v: bytes):
    st.session_state["recorded_audio"] = v

def clear_recorded_audio():
    st.session_state.pop("recorded_audio", None)

def clear_report():
    st.session_state.pop("report", None)
    st.session_state.pop("transcript", None)
    clear_recorded_audio()
