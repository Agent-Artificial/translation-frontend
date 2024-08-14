import json
import torch
import base64
import io
from fastapi import APIRouter, Request
from loguru import logger


router = APIRouter()


@router.post("/torch")
async def get_torch(request: Request):
    audio_data = base64.b64decode(await request.body())
    logger.info(audio_data.decode("utf-8"))
    return audio_data.decode("utf-8")
