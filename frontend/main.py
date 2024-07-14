# component_library/main.py
import os
import shutil
from loguru import logger
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from .routes.language_route import router as language_router
from .routes.mode_options import router as mode_options
from .routes.translation_route import router as translation_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the new router
app.include_router(language_router)
app.include_router(mode_options)
app.include_router(translation_router)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="./static"), name="static")

@app.get("/")
def index():
    return templates.TemplateResponse("main.html", {"request": {}})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("frontend.main:app", host="0.0.0.0", port=5700, reload=True)
    
