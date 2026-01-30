from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from web.services import schedule_service

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")

@router.get("/")
async def list_page(request: Request, date: str = "today"):
    schedules = schedule_service.list_schedules(date)
    return templates.TemplateResponse("schedule/list.html", {
        "request": request,
        "schedules": schedules,
        "current_date": date
    })

@router.post("/add")
async def add(date: str = Form(...), time: str = Form(...), event: str = Form(...)):
    schedule_service.add_schedule(date, time, event)
    return RedirectResponse(url="/schedule", status_code=303)

@router.post("/delete/{id}")
async def delete(id: int):
    schedule_service.delete_schedule(id)
    return RedirectResponse(url="/schedule", status_code=303)
