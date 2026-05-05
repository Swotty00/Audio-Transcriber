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
    


def send_text_to_backend(text, relator):
    url = "http://localhost:8000/structure-report"
    data = {"text": text, "relator": relator}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()
        return {"error": f"Erro no servidor: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}