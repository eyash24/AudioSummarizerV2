from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
import tempfile
import shutil
import os

from utils import voice_recognition, summarise

api = FastAPI()

class Response(BaseModel):
    summary: Optional[str] = None
    transcript: Optional[str] = None
    error: Optional[str] = None


from fastapi import FastAPI, File, UploadFile
import tempfile
import os
from typing import List

@api.post("/audio-summary/", response_model=Response)
async def audio_summary(file: UploadFile = File(...)):
    try:
        # Save uploaded file to a temporary path
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        
        transcript = voice_recognition(tmp_path)
        summary = summarise(transcript)

        # transcript = "This is a dummy transcript."  # Placeholder for actual transcription
        # summary = "This is a dummy summary."  # Placeholder for actual summarization

        # Clean up temp file
        os.remove(tmp_path)
        response = Response(transcript=transcript, summary=summary)

        return response

    except Exception as e:
        return Response(error=str(e))
