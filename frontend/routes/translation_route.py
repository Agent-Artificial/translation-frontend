import base64
import json
import binascii
from fastapi import APIRouter, Request, Form, HTTPException, File, UploadFile
from .process_audio import process_audio_request, process_audio_response
from .process_text import process_text_request, process_text_response
from fastapi.templating import Jinja2Templates
from typing import Optional
from loguru import logger
import requests

from frontend.routes.audio_route import AUDIO_SOURCE

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.post("/translate")
async def get_translate(
    request: Request, 
    textInputArea: Optional[str] = Form(default=None),
    audioData: UploadFile = File(default=None),
    inputModeOptions: str = Form(default=None),
    outputModeOptions: str = Form(...),
    sourceLanguageOptions: str = Form(...),
    targetLanguageOptions: str = Form(...)
):
    print(f"Received form data: textInputArea={textInputArea}, inputModeOptions={inputModeOptions}, outputModeOptions={outputModeOptions}, sourceLanguageOptions={sourceLanguageOptions}, targetLanguageOptions={targetLanguageOptions}")
    task_string = ""        
    
    if not inputModeOptions:
        if outputModeOptions == "text":
            task_string = "speech2text"
        elif outputModeOptions == "audio":
            task_string = "speech2speech"
    elif inputModeOptions == "audio":
        if outputModeOptions == "audio":
            task_string = "speech2speech"
        elif outputModeOptions == "text":
            task_string = "speech2text"
    elif inputModeOptions == "text":
        if outputModeOptions == "text":
            task_string = "text2text"
        elif outputModeOptions == "audio":
            task_string = "text2speech"

    data_request = None
    if task_string.startswith("speech"):
        data_request = await process_audio_request(audioData, task_string, sourceLanguageOptions, targetLanguageOptions)
    else:
        data_request = process_text_request(textInputArea, task_string, targetLanguageOptions, sourceLanguageOptions)
    print(f"Sending request")
    url = "https://miner-cellium.ngrok.app/modules/translation/process"
    translation_request = data_request
    try:
        response = requests.post(url, json=translation_request, timeout=30)
        response.raise_for_status()
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text[50:]}")
        
        if task_string.endswith("text"):
            return process_text_response(request, response, templates)
        else:
            return await process_audio_response(request, response, templates)
    except requests.RequestException as e:
        print(f"Request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation service error: {str(e)}")