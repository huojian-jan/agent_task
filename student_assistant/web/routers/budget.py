from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from web.services import budget_service

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")

@router.get("/")
async def list_page(request: Request):
    records = budget_service.list_records()
    summary = budget_service.get_monthly_summary()
    return templates.TemplateResponse("budget/list.html", {
        "request": request,
        "records": records,
        "summary": summary
    })

@router.post("/add")
async def add(
    type: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    note: str = Form("")
):
    budget_service.add_record(type, amount, category, note)
    return RedirectResponse(url="/budget", status_code=303)

@router.post("/delete/{id}")
async def delete(id: int):
    budget_service.delete_record(id)
    return RedirectResponse(url="/budget", status_code=303)

@router.get("/stats")
async def stats_page(request: Request):
    stats = budget_service.get_stats()
    return templates.TemplateResponse("budget/stats.html", {
        "request": request,
        "stats": stats
    })
