import sys
from pathlib import Path

try:
    from tools import course_cli
except ImportError:
    BASE_DIR = Path(__file__).parent.parent.parent
    sys.path.append(str(BASE_DIR))
    from tools import course_cli

def get_today_courses():
    return course_cli.query_courses(date="today")["data"]

def list_courses(weekday=None):
    return course_cli.query_courses(weekday=weekday)["data"]
