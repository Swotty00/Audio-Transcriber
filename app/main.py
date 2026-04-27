from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from config.logging_setup import setup_logging
from services.pipeline_service import PipelineService

setup_logging()

app = FastAPI(title="Audio Transcriber")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_pipeline = PipelineService()


@app.get("/health")
def health():
    return {"status": "ok", "model_ready": _pipeline._transcription.is_ready()}


@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Arquivo de áudio vazio.")

    suffix = f".{file.filename.rsplit('.', 1)[-1]}" if file.filename else ".wav"

    transcript = _pipeline.run_from_bytes(audio_bytes, suffix=suffix)

    return {
        "filename": file.filename,
        "duration": transcript.duration,
        "transcription": transcript.full_text,
        "segments": [
            {"start": s.start, "end": s.end, "text": s.text, "confidence": s.confidence}
            for s in transcript.segments
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
