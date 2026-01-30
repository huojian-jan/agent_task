import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    from config import COURSE_FILE
except ImportError:
    sys.path.append(str(Path(__file__).parent.parent))
    from config import COURSE_FILE

DEFAULT_COURSES = [
    {"weekday": 0, "time": "08:00-09:40", "name": "高等数学", "location": "A301"},
    {"weekday": 0, "time": "14:00-15:40", "name": "大学物理", "location": "B102"},
    {"weekday": 1, "time": "10:00-11:40", "name": "线性代数", "location": "A205"},
    {"weekday": 2, "time": "08:00-09:40", "name": "大学英语", "location": "C303"},
    {"weekday": 2, "time": "14:00-15:40", "name": "计算机导论", "location": "D401"},
    {"weekday": 3, "time": "14:00-15:40", "name": "体育(篮球)", "location": "体育馆"},
    {"weekday": 4, "time": "08:00-11:40", "name": "Python程序设计", "location": "机房5"}
]

def load_data():
    if not COURSE_FILE.exists():
        # 初始化默认数据
        with open(COURSE_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_COURSES, f, ensure_ascii=False, indent=2)
        return DEFAULT_COURSES
    
    try:
        with open(COURSE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def get_weekday_from_date(date_str):
    if date_str == 'today':
        return datetime.now().weekday()
    elif date_str == 'tomorrow':
        return (datetime.now() + timedelta(days=1)).weekday()
    
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.weekday()
    except ValueError:
        return -1

def query_courses(date=None, weekday=None):
    data = load_data()
    target_weekday = -1
    
    if weekday:
        weekdays_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, 
            "friday": 4, "saturday": 5, "sunday": 6,
            "周一": 0, "周二": 1, "周三": 2, "周四": 3, 
            "周五": 4, "周六": 5, "周日": 6
        }
        target_weekday = weekdays_map.get(str(weekday).lower(), -1)
    elif date:
        target_weekday = get_weekday_from_date(date)
    
    if target_weekday == -1:
        return {"success": False, "message": "日期或星期格式无效"}
        
    results = [c for c in data if c['weekday'] == target_weekday]
    # 按时间排序
    results.sort(key=lambda x: x['time'])
    
    weekdays_zh = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    
    return {
        "success": True, 
        "weekday": weekdays_zh[target_weekday],
        "data": results
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="课程表查询工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    query_parser = subparsers.add_parser("query", help="查询课程")
    query_parser.add_argument("--date", help="日期 YYYY-MM-DD/today/tomorrow")
    query_parser.add_argument("--weekday", help="星期 monday/周一")
    
    args = parser.parse_args()
    
    if args.command == "query":
        print(json.dumps(query_courses(args.date, args.weekday), ensure_ascii=False))
    else:
        parser.print_help()
