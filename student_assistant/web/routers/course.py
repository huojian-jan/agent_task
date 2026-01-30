from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from web.services import course_service

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")

@router.get("/")
async def list_page(request: Request, weekday: str = "monday"):
    courses = course_service.list_courses(weekday)
    return templates.TemplateResponse("course/list.html", {
        "request": request,
        "courses": courses,
        "current_weekday": weekday
    })
