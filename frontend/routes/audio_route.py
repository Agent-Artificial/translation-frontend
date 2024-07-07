from fastapi import APIRouter, Request, File, Form
from fastapi.templating import Jinja2Templates


from frontend.routes.process_audio import process_audio_request, process_audio_response
from frontend.routes.process_text import process_text_response


router = APIRouter()
templates = Jinja2Templates(directory="templates")

AUDIO_SOURCE = "static/audio/output.wav"

@router.post("/translate-audio")
async def send_audio(
    request: Request,
    audio_data: bytes = File(...), 
    outputModeOptions: str = Form(default=''),
    targetLanguageOptions: str = Form(default=''),
    sourceLanguageOptions: str = Form(default='')
):
    task_string = "speech2text" if outputModeOptions == "text" else "text2speech"
    response = process_audio_request(
        audio_data,
        task_string,
        sourceLanguageOptions,
        targetLanguageOptions
    )
    return (
        process_text_response(request, response, templates)
        if outputModeOptions == "text"
        else process_audio_response(request, response, templates)
    )