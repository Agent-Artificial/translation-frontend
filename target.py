from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from loguru import logger
import requests
import json
import io
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MinerData(BaseModel):
    input: str
    task_string: str
    target_language: str
    source_language: str

class MinerRequest(BaseModel):
    data: MinerData

@app.post("/")
async def index(request: MinerRequest):
    input_data = request.data.input

    audio = base64.b64decode(input_data.encode('utf-8'))
    
    print(audio)
    
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("target:app", host="0.0.0.0", port=5785, reload=True)
    