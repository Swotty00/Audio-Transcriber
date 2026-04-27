import requests

def send_to_backend(audio_bytes):
    url = "http://localhost:8000/process-audio"
    files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
    try:
        response = requests.post(url, files=files)
        if response.status_code == 200:
            return response.json()
        return {"error": f"Erro no servidor: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}