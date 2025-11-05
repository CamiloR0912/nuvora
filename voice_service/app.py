from fastapi import FastAPI, UploadFile, File
import whisper
import tempfile

app = FastAPI()
model = whisper.load_model("base")  # versión local, también puede ser "tiny"

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    result = model.transcribe(tmp_path, language="es")
    return {"text": result["text"]}
