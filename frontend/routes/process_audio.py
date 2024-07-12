import base64
import numpy
import struct
import io
import base64
import json
import torch
from pathlib import Path
from loguru import logger
from tempfile import SpooledTemporaryFile
from requests import Request, Response
from fastapi.templating import Jinja2Templates


AUDIO_SOURCE = "static/audio/output.wav"


def numpy_to_bytes(speech_output):
    return speech_output.tobytes()


# If your output is a list of floats
def list_to_bytes(speech_output):
    return struct.pack(f'{len(speech_output)}f', *speech_output)


async def process_audio_request(
    audioData: str,
    task_string: str,
    sourceLanguageOptions: str,
    targetLanguageOptions: str
):
    encoded_audio = audioData
    logger.debug(f"Audio data: {encoded_audio.read()[:20]}..")
       
    target_language = targetLanguageOptions.replace("\\", "").replace("\"", "")
    source_language = sourceLanguageOptions.replace("\\", "").replace("\"", "")
    return {
        "data": {
            "input": encoded_audio,
            "task_string": task_string,
            "target_language": target_language,
            "source_language": source_language,
        }
    }
    
def process_audio_response(
    request: Request,
    response: Response,
    templates: Jinja2Templates    
):
    print(response.text)
    with open(AUDIO_SOURCE, "wb") as f:
        f.write(base64.decodebytes(response.text.encode('utf-8')))
    return templates.TemplateResponse(
        "components/audioOutput.html",
        {
            "request": request,
            "audio_url": AUDIO_SOURCE
        },
    )
    
