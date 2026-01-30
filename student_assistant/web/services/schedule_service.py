import sys
from pathlib import Path

# 导入 tools 模块
# 注意：在 web 运行时，sys.path 可能需要调整
try:
    from tools import schedule_cli
except ImportError:
    BASE_DIR = Path(__file__).parent.parent.parent
    sys.path.append(str(BASE_DIR))
    from tools import schedule_cli

def get_today_schedules():
    return schedule_cli.query_schedule("today")["data"]

def list_schedules(date="today"):
    return schedule_cli.query_schedule(date)["data"]

def add_schedule(date, time, event):
    return schedule_cli.add_schedule(date, time, event)

def delete_schedule(schedule_id):
    return schedule_cli.delete_schedule(schedule_id)
