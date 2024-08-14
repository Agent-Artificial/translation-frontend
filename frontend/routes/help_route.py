from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/help")
async def get_help(request: Request):
    return templates.TemplateResponse("components/help.html", {"request": request})