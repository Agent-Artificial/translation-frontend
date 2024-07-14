from fastapi import APIRouter, Request, Form, HTTPException, File, UploadFile
from .response_handler import ResponseHandler
from fastapi.templating import Jinja2Templates
from typing import Optional
from loguru import logger

templates = Jinja2Templates(directory="templates")

router = APIRouter()


class AudioProcessingError(Exception):
    """Failure while processing audio"""
    
class TextProcessingError(Exception):
    """Failure while processing text"""


@router.post("/translate")
async def get_translate(
    request: Request,
    textInputArea: Optional[str] = Form(default=None),
    audioData: Optional[UploadFile] = File(default=None),
    inputModeOptions: str = Form(default=None),
    outputModeOptions: str = Form(...),
    sourceLanguageOptions: str = Form(...),
    targetLanguageOptions: str = Form(...),
):
    request_handler = ResponseHandler()
    try:
        response = await request_handler.process_request(
            request=request,
            textInputArea=textInputArea,
            audioData=audioData,
            inputModeOptions=inputModeOptions,
            outputModeOptions=outputModeOptions,
            sourceLanguageOptions=sourceLanguageOptions,
            targetLanguageOptions=targetLanguageOptions
        )
        logger.debug(f"Response: {response}")
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

    return response