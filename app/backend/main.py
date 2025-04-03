from enum import IntEnum
from typing import List, Optional
from utils import voice_recognition, summarise

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

api = FastAPI()


def voice_to_text(path: str):
    try:
        transcript = voice_recognition(path)
        return transcript
    except:
        return HTTPException(status_code=404, detail="Path not found")


def text_summarise(text: str):
    try:
        summary = summarise(text)
        return summary
    except:
        return HTTPException()
