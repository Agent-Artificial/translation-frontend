import pytest
from fastapi import Request, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from unittest.mock import AsyncMock, patch, MagicMock
from frontend.routes.response_handler import ResponseHandler

@pytest.mark.parametrize(
    "inputModeOptions, outputModeOptions, sourceLanguageOptions, targetLanguageOptions, textInputArea, audioData, expected_task_string, expected_response",
    [
        ("audio", "text", "en", "fr", None, UploadFile(file="static/audio/audio_response.wav"), "speech2text", "processed_text_response"),
        ("text", "audio", "en", "fr", "Hello", None, "text2speech", "static/audio/audio_response.wav"),
        ("text", "text", "en", "fr", "Hello", None, "text2text", "processed_text_response"),
    ],
    ids=["audio_to_text", "text_to_audio", "text_to_text"]
)
@patch("frontend.routes.response_handler.requests.post")
@patch("frontend.routes.response_handler.Jinja2Templates.TemplateResponse")
@patch("frontend.routes.response_handler.AudioSegment.from_file")
@patch("frontend.routes.response_handler.base64.b64encode")
@patch("frontend.routes.response_handler.base64.b64decode")
@patch("frontend.routes.response_handler.torchaudio.save")
@patch("frontend.routes.response_handler.torch.load")
async def test_process_request(
    mock_torch_load,
    mock_torchaudio_save,
    mock_b64decode,
    mock_b64encode,
    mock_from_file,
    mock_template_response,
    mock_post,
    inputModeOptions,
    outputModeOptions,
    sourceLanguageOptions,
    targetLanguageOptions,
    textInputArea,
    audioData,
    expected_task_string,
    expected_response
):
    # Arrange
    handler = ResponseHandler()
    request = MagicMock(spec=Request)
    mock_post.return_value.status_code = 200
    mock_post.return_value.text = "response_text"
    mock_b64encode.return_value.decode.return_value = "encoded_audio"
    mock_b64decode.return_value = b"decoded_audio"
    mock_torch_load.return_value.cpu.return_value = "audio_tensor"
    mock_template_response.return_value = "template_response"

    # Act
    response = await handler.process_request(
        request,
        audioData=audioData,
        textInputArea=textInputArea,
        inputModeOptions=inputModeOptions,
        outputModeOptions=outputModeOptions,
        sourceLanguageOptions=sourceLanguageOptions,
        targetLanguageOptions=targetLanguageOptions,
    )

    # Assert
    assert handler.task_string == expected_task_string
    assert response == "template_response"

@pytest.mark.parametrize(
    "inputModeOptions, outputModeOptions, expected_task_string",
    [
        ("audio", "text", "speech2text"),
        ("text", "audio", "text2speech"),
        ("text", "text", "text2text"),
    ],
    ids=["audio_to_text", "text_to_audio", "text_to_text"]
)
def test_set_task_string(inputModeOptions, outputModeOptions, expected_task_string):
    # Arrange
    handler = ResponseHandler()

    # Act
    task_string = handler._set_task_string(inputModeOptions, outputModeOptions)

    # Assert
    assert task_string == expected_task_string

@pytest.mark.parametrize(
    "languageOption, expected_output",
    [
        ('\\"en\\"', 'en'),
        ('\\"fr\\"', 'fr'),
        ('\\"es\\"', 'es'),
    ],
    ids=["english", "french", "spanish"]
)
def test_process_languages(languageOption, expected_output):
    # Arrange
    handler = ResponseHandler()

    # Act
    processed_language = handler._process_languages(languageOption)

    # Assert
    assert processed_language == expected_output

@pytest.mark.parametrize(
    "textInputArea, expected_output",
    [
        ("Hello", "Hello"),
        ("Bonjour", "Bonjour"),
        ("Hola", "Hola"),
    ],
    ids=["english", "french", "spanish"]
)
def test_process_input_text(textInputArea, expected_output):
    # Arrange
    handler = ResponseHandler()

    # Act
    processed_text = handler._process_input_text(textInputArea)

    # Assert
    assert processed_text == expected_output

@pytest.mark.parametrize(
    "audioData, expected_output",
    [
        (b"audio_data", "encoded_audio"),
    ],
    ids=["audio_data"]
)
@patch("frontend.routes.response_handler.AudioSegment.from_file")
@patch("frontend.routes.response_handler.base64.b64encode")
def test_process_input_audio(mock_b64encode, mock_from_file, audioData, expected_output):
    # Arrange
    handler = ResponseHandler()
    mock_b64encode.return_value.decode.return_value = expected_output

    # Act
    processed_audio = handler._process_input_audio(audioData)

    # Assert
    assert processed_audio == expected_output

@pytest.mark.parametrize(
    "input_data, task_string, target_language, source_language, expected_output",
    [
        ("input_data", "task_string", "fr", "en", {"data": {"input": "input_data", "task_string": "task_string", "target_language": "fr", "source_language": "en"}}),
    ],
    ids=["construct_request"]
)
def test_construct_request(input_data, task_string, target_language, source_language, expected_output):
    # Arrange
    handler = ResponseHandler()

    # Act
    request_data = handler._construct_request(input_data, task_string, target_language, source_language)

    # Assert
    assert request_data == expected_output

@pytest.mark.parametrize(
    "b64encoded_request, url, response_text",
    [
        ({"data": "encoded_request"}, "http://example.com", "response_text"),
    ],
    ids=["make_request"]
)
@patch("frontend.routes.response_handler.requests.post")
def test_make_request(mock_post, b64encoded_request, url, response_text):
    # Arrange
    handler = ResponseHandler()
    mock_post.return_value.status_code = 200
    mock_post.return_value.text = response_text

    # Act
    response = handler._make_request(b64encoded_request, url)

    # Assert
    assert response.text == response_text

@pytest.mark.parametrize(
    "response_data, expected_output",
    [
        (b"encoded_text", "decoded_text"),
    ],
    ids=["process_text_response"]
)
@patch("frontend.routes.response_handler.base64.b64decode")
def test_process_text_response(mock_b64decode, response_data, expected_output):
    # Arrange
    handler = ResponseHandler()
    mock_b64decode.return_value.decode.return_value = expected_output

    # Act
    processed_text = handler._process_text_response(response_data)

    # Assert
    assert processed_text == expected_output

@pytest.mark.parametrize(
    "response_data, expected_output",
    [
        ("encoded_audio", "static/audio/audio_response.wav"),
    ],
    ids=["process_audio_response"]
)
@patch("frontend.routes.response_handler.torchaudio.save")
@patch("frontend.routes.response_handler.torch.load")
@patch("frontend.routes.response_handler.base64.b64decode")
def test_process_audio_response(mock_b64decode, mock_torch_load, mock_torchaudio_save, response_data, expected_output):
    # Arrange
    handler = ResponseHandler()
    mock_b64decode.return_value = b"decoded_audio"
    mock_torch_load.return_value.cpu.return_value = "audio_tensor"

    # Act
    response_path = handler._process_audio_response(response_data)

    # Assert
    assert response_path == expected_output

@pytest.mark.parametrize(
    "task_string, response_data, expected_template",
    [
        ("text2text", "processed_text_response", "components/textOutput.html"),
        ("speech2text", "static/audio/audio_response.wav", "components/textOutput.html"),
    ],
    ids=["text_response", "audio_response"]
)
@patch("frontend.routes.response_handler.Jinja2Templates.TemplateResponse")
def test_return_template_response(mock_template_response, task_string, response_data, expected_template):
    # Arrange
    handler = ResponseHandler()
    handler.task_string = task_string
    request = MagicMock(spec=Request)
    mock_template_response.return_value = "template_response"

    # Act
    response = handler._return_template_response(request, response_data)

    # Assert
    assert response == "template_response"
    mock_template_response.assert_called_with(expected_template, {"request": request, "text" if task_string.endswith("text") else "audio_url": response_data})
