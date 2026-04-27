import streamlit as st
from audio_recorder import audiorecorder

st.title("Audio Recorder")
audio = audiorecorder("Click to record", "Click to stop recording", custom_style={"backgroundColor": "lightblue"})

if len(audio) > 0:
    st.audio(audio.export().read())

    audio.export("audio.wav", format="wav")

    st.write(f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds")