import pytest
import requests
import io
from unittest.mock import Mock, patch, Mock
from fastapi import UploadFile
from pydub import AudioSegment
from frontend.routes.response_handler import RequestHandler 

@pytest.fixture
def request_handler():
    return RequestHandler()

def test_process_languages(request_handler):
    assert request_handler._process_languages("\"english\\") == "english"

def test_process_input_text(request_handler):
    text = "Hello, world!"
    result = request_handler._process_input_text(text)
    assert result == text

def test_process_input_audio(request_handler):
    mock_audio = Mock(spec=UploadFile)
    mock_audio.read.return_value = b"fake audio data"
    
    with patch.object(AudioSegment, 'from_file') as mock_from_file:
        mock_audio_segment = Mock()
        mock_from_file.return_value = mock_audio_segment
        mock_audio_segment.export.side_effect = lambda buffer, format: buffer.write(b"processed audio data")
        
        result = request_handler._process_input_audio(mock_audio)
        
    assert result == b"processed audio data"

def test_b64encode_request(request_handler):
    input_data = "test input"
    task_string = "text2text"
    target_language = "french"
    source_language = "english"
    
    result = request_handler._b64encode_request(input_data, task_string, target_language, source_language)
    
    assert "data" in result
    assert "input" in result["data"]
    assert "task_string" in result["data"]
    assert "target_language" in result["data"]
    assert "source_language" in result["data"]
    assert result["data"]["task_string"] == task_string
    assert result["data"]["target_language"] == target_language
    assert result["data"]["source_language"] == source_language

def test_make_request(request_handler):
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"data": {"output": "test output"}}
    
    with patch.object(requests, 'post') as mock_post:
        mock_post.return_value = mock_response
        result = request_handler._make_request({"test": "data"}, "https://miner-cellium.ngrok.app/modules/translation/process")
    
    assert result == {"data": {"output": "test output"}}

def test_b64decode_response(request_handler):
    response = {"data": {"output": "dGVzdCBvdXRwdXQ="}}  # "test output" in base64
    result = request_handler._b64decode_response(response)
    assert result == b"test output"

def test_process_text_response(request_handler):
    response_data = b"test output"
    result = request_handler._process_text_response(response_data)
    assert result == "test output"

def test_process_request(request_handler):
    mock_request = Mock()
    mock_audio_data = Mock(spec=UploadFile)
    mock_audio_data.read.return_value = b"fake audio data"
    
    with patch.object(RequestHandler, '_make_request') as mock_make_request, \
         patch.object(RequestHandler, '_process_audio_response') as mock_process_audio, \
         patch.object(RequestHandler, '_return_template_response') as mock_return_template:
        
        mock_make_request.return_value = {"data": {"output": "dGVzdCBvdXRwdXQ="}}
        mock_process_audio.return_value = "statis/audio/audio.wav"
        mock_return_template.return_value = "template response"
        
        result = request_handler.process_request(
            request=mock_request,
            audioData=mock_audio_data,
            inputModeOptions="audio",
            outputModeOptions="audio",
            sourceLanguageOptions="english",
            targetLanguageOptions="french"
        )
    
    assert result == "template response"
    assert request_handler.task_string == "speech2speech"
    assert request_handler.source_language == "english"
    assert request_handler.target_language == "french"

# Add more tests as needed for other methods and edge cases