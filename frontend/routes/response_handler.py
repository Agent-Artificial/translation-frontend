import io
import json
import base64
import requests
import torchaudio
import torch
from pydub import AudioSegment
from fastapi import Request, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from typing import Optional
from loguru import logger


class ResponseHandler:
    def __init__(self):
        self.client = requests.Session()
        self.templates = Jinja2Templates(directory="templates")
        self.url = "https://miner-cellium.ngrok.app/modules/translation/process"
        self.task_string = None
        self.target_language = None
        self.source_language = None
        self.request = None
        self.response = None
        
    async def process_request(
        self,
        request: Request,
        audioData: Optional[UploadFile] = None,
        textInputArea: Optional[str] = None,
        inputModeOptions: str = None,
        outputModeOptions: str = None,
        sourceLanguageOptions: str = None,
        targetLanguageOptions: str = None,
    ):
        try:
            self._set_task_string(inputModeOptions, outputModeOptions)
            self.source_language = self._process_languages(sourceLanguageOptions)
            self.target_language = self._process_languages(targetLanguageOptions)
            
            if self.task_string.startswith("speech"):
                input_data = self._process_input_audio(await audioData.read())
            else:
                input_data = self._process_input_text(textInputArea)
                
            encoded_request = self._construct_request(input_data, self.task_string, self.target_language, self.source_language)
            response = self._make_request(encoded_request, self.url)
            
            logger.debug(response.text[:50])
            if self.task_string.endswith("text"):
                processed_response = self._process_text_response(response.text)
            else:
                processed_response = self._process_audio_response(response.text)
            
            return self._return_template_response(request, processed_response)
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

    def _set_task_string(self, inputModeOptions, outputModeOptions):
        mode_map = {
            "audio": "speech",
            "text": "text"
        }
        self.task_string = f"{mode_map[inputModeOptions]}2{mode_map[outputModeOptions]}"
        return self.task_string

    def _process_languages(self, languageOption: str):
        return languageOption.replace("\\", "").replace("\"", "")
    
    def _process_input_text(self, textInputArea: str):
        return textInputArea        
    
    def _process_input_audio(self, audioData: bytes, audio_path: Optional[str] = None):
        
        audio_path = audio_path or "static/audio/audio_request.wav"
        audio = AudioSegment.from_file(io.BytesIO(audioData), format="webm")
        audio.export(audio_path, format="wav")

        with open(audio_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
        
    def _construct_request(self, input_data, task_string, target_language, source_language):
        return {
            "data": {
                "input": input_data,
                "task_string": task_string,
                "target_language": target_language,
                "source_language": source_language,
            }
        }
        
    def _make_request(self, b64encoded_request, url):
        response = requests.post(url, json=b64encoded_request, timeout=30)
        response.raise_for_status()
        return response
            
    def _process_text_response(self, response_data):
        return base64.b64decode(response_data).decode("utf-8")
        
    def _process_audio_response(self, response_data):
        response_path = "static/audio/audio_response.wav"
        unencoded = base64.b64decode(response_data)
        audio = torch.load(io.BytesIO(unencoded)).cpu()
    
        logger.debug(audio[:30])
        torchaudio.save(
            src=audio,
            uri=response_path, 
            sample_rate=16000,
            format="wav"
        )
        logger.debug("audio saved")
        return response_path
    
    def _return_template_response(self, request, response_data):
        if self.task_string.endswith("text"):
            return self.templates.TemplateResponse(
                "components/textOutput.html",
                {
                    "request": request,
                    "text": response_data
                }
            )
        else:
            return self.templates.TemplateResponse(
                "components/audioOutput.html",
                {
                    "request": request,
                    "audio_url": response_data
                }
            )


def text2text(text_input, handler):
    
    request_data = {
        "data": {
            "input": text_input,
            "task_string": "text2text",
            "target_language": "french",
            "source_language": "english",
        }
    }
   
    response = handler._make_request(request_data, "https://miner-cellium.ngrok.app/modules/translation/process")
    result = base64.b64decode(response.text).decode("utf-8")
    
    logger.debug(result)
   
   
def text2speech(text_input, handler):
    
    request_data = {
        "data": {
            "input": text_input,
            "task_string": "text2speech",
            "target_language": "french",
            "source_language": "english",
        }
    }
   
    response = handler._make_request(request_data, "https://miner-cellium.ngrok.app/modules/translation/process")
    
    unencoded = base64.b64decode(response.content.decode("utf-8"))
    
    audio = torch.load(io.BytesIO(unencoded)).cpu()
    
    logger.debug(audio[:30])
    torchaudio.save(
        src=audio,
        uri="static/audio/audio_response.wav", 
        sample_rate=16000,
        format="wav"
    )
    logger.debug("audio saved")
    
    
def speech2text(audio_path, handler):
    with open(audio_path, "rb") as f:
        audio_data = f.read()
        base64_audio = base64.b64encode(audio_data).decode("utf-8")
    request_data = {
        "data": {
            "input": base64_audio,
            "task_string": "speech2text",
            "target_language": "french",
            "source_language": "english",
        }
    }
    
    response = handler._make_request(request_data, "https://miner-cellium.ngrok.app/modules/translation/process")
    
    unencoded = base64.b64decode(response.text).decode("utf-8")
    logger.debug(str(unencoded)[0:100])
    
    
def speech2speech(audio_path, handler):
    with open(audio_path, "rb") as f:
        audio_data = f.read()
        base64_audio = base64.b64encode(audio_data).decode("utf-8")
    request_data = {
        "data": {
            "input": base64_audio,
            "task_string": "speech2speech",
            "target_language": "french",
            "source_language": "english",
        }
    }

    response = handler._make_request(request_data, "https://miner-cellium.ngrok.app/modules/translation/process")

    unencoded = base64.b64decode(response.content.decode("utf-8"))
    
    audio = torch.load(io.BytesIO(unencoded)).cpu()
    
    logger.debug(audio[:30])
    torchaudio.save(
        src=audio,
        uri="static/audio/audio_response.wav", 
        sample_rate=16000,
        format="wav"
    )
    logger.debug("audio saved")

            
if __name__ == "__main__":
    handler = ResponseHandler()
    audio_path = "static/audio/audio_request.wav"
    text_input = "the cat is black"
    text2text(text_input, handler)
    text2speech(text_input, handler)
    speech2text(audio_path, handler)
    speech2speech(audio_path, handler)



    
