import json
import torchaudio
import torch
import base64
import io
from fastapi import APIRouter, Request
from loguru import logger


router = APIRouter()


@router.post("/torch")
async def get_torch(request: Request):
    response_path = "static/audio/audio_response.wav"
    unencoded = base64.b64decode(await request.body())
    audio = torch.load(io.BytesIO(unencoded)).cpu()

    logger.debug(audio[:30])
    torchaudio.save(src=audio, uri=response_path, sample_rate=16000, format="wav")
    logger.debug("audio saved")
    
    with open(response_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")