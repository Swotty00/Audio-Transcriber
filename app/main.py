from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import io
import json
import wave
from vosk import Model, KaldiRecognizer
import os

app = FastAPI()

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models")
model = Model(MODEL_PATH)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    audio_data = await file.read()
    
    # 2. Abrir o áudio usando o módulo wave (Vosk precisa de WAV puro)
    with wave.open(io.BytesIO(audio_data), "rb") as wf:
        # Verifica se o áudio está no formato que o Vosk espera
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            return {"error": "O áudio deve ser WAV Mono (PCM 16-bit)."}

        # 3. Inicializar o reconhecedor com a taxa de amostragem do arquivo
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True) # Opcional: para retornar timestamps das palavras

        # 4. Processar o áudio
        transcription = ""
        while True:
            data = wf.readframes(4000) # Lê o áudio em pedaços
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                pass # Pode capturar resultados parciais aqui se desejar

        # 5. Pegar o resultado final
        result_json = json.loads(rec.FinalResult())
        transcription = result_json.get("text", "")

    return {
        "filename": file.filename,
        "transcription": transcription,
        "ai_analysis": "A IA analisou seu texto e concluiu que o projeto será um sucesso!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)