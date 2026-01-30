from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sys

# 确保路径正确
BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR))

from web.routers import schedule, budget, course
from web.services import schedule_service, budget_service, course_service

app = FastAPI(title="大学生小秘书 - 数据管理")

# 挂载静态文件和模板
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

# 注册路由
app.include_router(schedule.router, prefix="/schedule", tags=["日程"])
app.include_router(budget.router, prefix="/budget", tags=["生活费"])
app.include_router(course.router, prefix="/course", tags=["课程"])

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "today_schedules": schedule_service.get_today_schedules(),
        "today_courses": course_service.get_today_courses(),
        "budget_summary": budget_service.get_monthly_summary()
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
