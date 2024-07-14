import io
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
        """
        Initializes a new instance of the `ResponseHandler` class.

        This constructor sets up the necessary attributes for the `ResponseHandler` object. It creates a new `requests.Session` object to handle HTTP requests, initializes the `templates` attribute with a `Jinja2Templates` object that loads templates from the "templates" directory, sets the `url` attribute to the specified URL for processing translations, and initializes the other attributes (`task_string`, `target_language`, `source_language`, `request`, `response`) to `None`.

        Parameters:
            None

        Returns:
            None
        """
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
        """
        A function that processes the request asynchronously, handling various input data based on task string and modes, making requests, processing responses, and returning template responses.

        Args:
            request: Request object.
            audioData: Optional UploadFile object containing audio data (default is None).
            textInputArea: Optional str for text input (default is None).
            inputModeOptions: str representing input mode options.
            outputModeOptions: str representing output mode options.
            sourceLanguageOptions: str representing source language options.
            targetLanguageOptions: str representing target language options.

        Returns:
            Response based on the request and processed data.
        """
        try:
            self._set_task_string(inputModeOptions, outputModeOptions)
            self.source_language = self._process_languages(sourceLanguageOptions)
            self.target_language = self._process_languages(targetLanguageOptions)

            if self.task_string.startswith("speech"):
                input_data = self._process_input_audio(await audioData.read())
            else:
                input_data = self._process_input_text(textInputArea)

            encoded_request = self._construct_request(
                input_data, self.task_string, self.target_language, self.source_language
            )
            response = self._make_request(encoded_request, self.url)

            logger.debug(response.text[:50])
            if self.task_string.endswith("text"):
                processed_response = self._process_text_response(response.text)
            else:
                processed_response = self._process_audio_response(response.text)

            return self._return_template_response(request, processed_response)

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error processing request: {str(e)}"
            )

    def _set_task_string(self, inputModeOptions, outputModeOptions):
        """
        A function that sets the task string based on the input mode and output mode options provided.

        Args:
            inputModeOptions: The input mode option.
            outputModeOptions: The output mode option.

        Returns:
            The generated task string.
        """
        mode_map = {"audio": "speech", "text": "text"}
        self.task_string = f"{mode_map[inputModeOptions]}2{mode_map[outputModeOptions]}"
        return self.task_string

    def _process_languages(self, languageOption: str):
        """
        Remove backslashes and double quotes from the given language option string.

        Args:
            languageOption (str): The language option string to process.

        Returns:
            str: The processed language option string with backslashes and double quotes removed.
        """
        return languageOption.replace("\\", "").replace('"', "")

    def _process_input_text(self, textInputArea: str):
        """
        Process the input text by returning the same text.

        Args:
            textInputArea (str): The input text to be processed.

        Returns:
            str: The same input text that was passed as an argument.
        """
        return textInputArea

    def _process_input_audio(self, audioData: bytes, audio_path: Optional[str] = None):
        """
        Processes input audio data, converts it to WAV format, and returns the base64 encoded audio data.
        
        Args:
            audioData (bytes): The input audio data to be processed.
            audio_path (str, optional): The path to save the processed audio file. Defaults to "static/audio/audio_request.wav".
        
        Returns:
            str: The base64 encoded audio data.
        """
        audio_path = audio_path or "static/audio/audio_request.wav"
        audio = AudioSegment.from_file(io.BytesIO(audioData), format="webm")
        audio.export(audio_path, format="wav")

        with open(audio_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _construct_request(
        self, input_data, task_string, target_language, source_language
    ):
        """
        Constructs a request dictionary with the provided input data, task string, target language, and source language.

        Args:
            input_data: The input data for the request.
            task_string: The task string for the request.
            target_language: The target language for the request.
            source_language: The source language for the request.

        Returns:
            dict: A dictionary containing the constructed request data.

        """
        return {
            "data": {
                "input": input_data,
                "task_string": task_string,
                "target_language": target_language,
                "source_language": source_language,
            }
        }

    def _make_request(self, b64encoded_request, url):
        """
        Sends a POST request to the specified URL with the given base64 encoded request data.
        
        Args:
            b64encoded_request (str): The base64 encoded request data.
            url (str): The URL to send the request to.
        
        Returns:
            requests.Response: The response object from the request.
        
        Raises:
            requests.exceptions.HTTPError: If the response status code is not successful.
        
        Description:
            This function sends a POST request to the specified URL with the given base64 encoded request data.
            It uses the `requests` library to make the request and sets a timeout of 30 seconds.
            If the response status code is not successful (200-299), it raises an `HTTPError`.
            Otherwise, it returns the response object.
        """
        response = requests.post(url, json=b64encoded_request, timeout=30)
        response.raise_for_status()
        return response

    def _process_text_response(self, response_data):
        """
        Decode the base64-encoded response data and return the decoded text.

        Args:
            response_data (bytes): The base64-encoded response data.

        Returns:
            str: The decoded text.
        """
        return base64.b64decode(response_data).decode("utf-8")

    def _process_audio_response(self, response_data):
        """
        Processes the audio response data and saves it as a WAV file.

        Args:
            response_data (str): The base64 encoded audio response data.

        Returns:
            str: The path to the saved WAV file.
        """
        response_path = "static/audio/audio_response.wav"
        unencoded = base64.b64decode(response_data)
        audio = torch.load(io.BytesIO(unencoded)).cpu()

        logger.debug(audio[:30])
        torchaudio.save(src=audio, uri=response_path, sample_rate=16000, format="wav")
        logger.debug("audio saved")
        return response_path

    def _return_template_response(self, request, response_data):
        """
        Returns a TemplateResponse object based on the task string.

        Args:
            request (Request): The request object.
            response_data (str): The response data.

        Returns:
            TemplateResponse: A TemplateResponse object with the appropriate template and context.

        Raises:
            None
        """
        if self.task_string.endswith("text"):
            return self.templates.TemplateResponse(
                "components/textOutput.html",
                {"request": request, "text": response_data},
            )
        else:
            return self.templates.TemplateResponse(
                "components/audioOutput.html",
                {"request": request, "audio_url": response_data},
            )


def text2text(text_input, handler):
    """
    Converts the given text input to text in French using the specified handler.

    Args:
        text_input (str): The text input to be converted to text.
        handler (object): The handler object used to make the request to the translation API.

    Returns:
        None

    Description:
        This function creates a request data dictionary with the input text, task string, target language,
        and source language. The request data is sent to the specified URL using the handler's
        `_make_request` method. The response is decoded from base64 and logged using the logger.

    Note:
        The translation API endpoint used is "https://miner-cellium.ngrok.app/modules/translation/process".

     """
    request_data = {
        "data": {
            "input": text_input,
            "task_string": "text2text",
            "target_language": "french",
            "source_language": "english",
        }
    }

    response = handler._make_request(
        request_data, "https://miner-cellium.ngrok.app/modules/translation/process"
    )
    result = base64.b64decode(response.text).decode("utf-8")

    logger.debug(result)


def text2speech(text_input, handler):
    """
    Converts the given text input to speech in French using the specified handler.

    Args:
        text_input (str): The text input to be converted to speech.
        handler (object): The handler object used to make the request to the translation API.

    Returns:
        None
    """
    request_data = {
        "data": {
            "input": text_input,
            "task_string": "text2speech",
            "target_language": "french",
            "source_language": "english",
        }
    }

    response = handler._make_request(
        request_data, "https://miner-cellium.ngrok.app/modules/translation/process"
    )

    unencoded = base64.b64decode(response.content.decode("utf-8"))

    audio = torch.load(io.BytesIO(unencoded)).cpu()

    logger.debug(audio[:30])
    torchaudio.save(
        src=audio,
        uri="static/audio/audio_response.wav",
        sample_rate=16000,
        format="wav",
    )
    logger.debug("audio saved")


def speech2text(audio_path, handler):
    """
    Converts speech to text using the provided audio file path and handler.

    Args:
        audio_path (str): The path to the audio file.
        handler (object): The handler object used to make the request.

    Returns:
        None

    Raises:
        None

    Description:
        This function reads the audio file specified by `audio_path` and encodes it in base64.
        It then creates a request data dictionary with the encoded audio, task string, target language,
        and source language. The request data is sent to the specified URL using the handler's
        `_make_request` method. The response is decoded from base64 and logged using the logger.

    """
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

    response = handler._make_request(
        request_data, "https://miner-cellium.ngrok.app/modules/translation/process"
    )

    unencoded = base64.b64decode(response.text).decode("utf-8")
    logger.debug(str(unencoded)[0:100])


def speech2speech(audio_path, handler):
    """
    Converts speech from the input audio file to speech in French using the specified handler.

    Args:
        audio_path (str): The path to the input audio file.
        handler (object): The handler object used to make the request to the translation API.

    Returns:
        None

    Raises:
        None

    Description:
        This function reads the audio data from the input audio file, encodes it in base64, and sends a request to the translation API to convert the speech to French. The response from the API is decoded and loaded into a torch tensor, which is then saved as a WAV file in the "static/audio/audio_response.wav" directory.

    Note:
        The translation API endpoint used is "https://miner-cellium.ngrok.app/modules/translation/process".

    """
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

    response = handler._make_request(
        request_data, "https://miner-cellium.ngrok.app/modules/translation/process"
    )

    unencoded = base64.b64decode(response.content.decode("utf-8"))

    audio = torch.load(io.BytesIO(unencoded)).cpu()

    logger.debug(audio[:30])
    torchaudio.save(
        src=audio,
        uri="static/audio/audio_response.wav",
        sample_rate=16000,
        format="wav",
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
