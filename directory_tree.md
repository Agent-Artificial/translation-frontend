├── Dockerfile
├── README.md
├── assets
│   ├── microphone-off.svg
│   ├── microphone.svg
│   ├── swap.svg
│   └── upload.svg
├── docker-compose.yml
├── files
│   └── blob
├── frontend
│   ├── app.py
│   ├── main.py
│   └── routes
│       ├── language_route.py
│       ├── mode_options.py
│       ├── process_audio.py
│       ├── process_text.py
│       └── translation_route.py
├── output
│   └── audio_request.wav.text
├── poetry.lock
├── pyproject.toml
├── setup.cfg
├── static
│   ├── audio
│   │   └── audio_request.wav
│   └── text
├── templates
│   ├── components
│   │   ├── audioInput.html
│   │   ├── audioOutput.html
│   │   ├── audioPlayer.html
│   │   ├── dropZone.html
│   │   ├── inputContent.html
│   │   ├── inputModeDropdown.html
│   │   ├── outputContent.html
│   │   ├── outputModeDropdown.html
│   │   ├── sourceLanguageDropdown.html
│   │   ├── sourceTargetFlipper.html
│   │   ├── startRecording.html
│   │   ├── startRecordingButton.html
│   │   ├── targetLanguageDropdown.html
│   │   ├── textInput.html
│   │   ├── textOutput.html
│   │   └── translateButton.html
│   ├── index.html
│   ├── main.html
│   └── shared
│       └── _base.html
├── testing.py
├── tests
│   └── test_audio_chat.py
└── walkdir.py