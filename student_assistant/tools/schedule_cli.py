import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 适配直接运行和模块导入路径
try:
    from config import SCHEDULE_FILE
except ImportError:
    # 如果作为脚本直接运行，尝试从上级目录导入
    sys.path.append(str(Path(__file__).parent.parent))
    from config import SCHEDULE_FILE

def load_data():
    if not SCHEDULE_FILE.exists():
        return []
    try:
        with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_data(data):
    with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_schedule(date, time, event, duration=60):
    data = load_data()
    
    # 生成新ID
    new_id = 1
    if data:
        new_id = max(item['id'] for item in data) + 1
    
    new_item = {
        "id": new_id,
        "date": date,
        "time": time,
        "event": event,
        "duration": duration, # 分钟
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    data.append(new_item)
    save_data(data)
    return {"success": True, "id": new_id, "message": "日程已添加", "data": new_item}

def query_schedule(date, time_range=None):
    data = load_data()
    results = []
    
    # 解析相对日期
    target_date = date
    if date == 'today':
        target_date = datetime.now().strftime("%Y-%m-%d")
    elif date == 'tomorrow':
        target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
    for item in data:
        if item['date'] == target_date:
            # 如果有时间范围筛选 (简单的字符串比较，实际项目应更严谨)
            if time_range:
                start, end = time_range.split('-')
                item_start = item['time']
                # 简单起见，只比较开始时间在范围内
                if start <= item_start <= end:
                    results.append(item)
            else:
                results.append(item)
                
    return {"success": True, "data": results}

def delete_schedule(schedule_id):
    data = load_data()
    new_data = [item for item in data if item['id'] != schedule_id]
    
    if len(new_data) == len(data):
        return {"success": False, "message": "未找到指定ID的日程"}
        
    save_data(new_data)
    return {"success": True, "message": "日程已删除"}

def update_schedule(schedule_id, time=None, event=None):
    data = load_data()
    found = False
    for item in data:
        if item['id'] == schedule_id:
            if time: item['time'] = time
            if event: item['event'] = event
            found = True
            break
            
    if not found:
        return {"success": False, "message": "未找到指定ID的日程"}
        
    save_data(data)
    return {"success": True, "message": "日程已更新"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="日程管理工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # add 命令
    add_parser = subparsers.add_parser("add", help="添加日程")
    add_parser.add_argument("--date", required=True, help="日期 YYYY-MM-DD")
    add_parser.add_argument("--time", required=True, help="时间 HH:MM")
    add_parser.add_argument("--event", required=True, help="事件内容")
    add_parser.add_argument("--duration", type=int, default=60, help="持续时间(分钟)")
    
    # query 命令
    query_parser = subparsers.add_parser("query", help="查询日程")
    query_parser.add_argument("--date", required=True, help="日期")
    query_parser.add_argument("--time-range", help="时间范围 HH:MM-HH:MM")
    
    # delete 命令
    del_parser = subparsers.add_parser("delete", help="删除日程")
    del_parser.add_argument("--id", type=int, required=True, help="日程ID")
    
    # update 命令
    up_parser = subparsers.add_parser("update", help="修改日程")
    up_parser.add_argument("--id", type=int, required=True, help="日程ID")
    up_parser.add_argument("--time", help="新时间")
    up_parser.add_argument("--event", help="新事件")
    
    args = parser.parse_args()
    
    if args.command == "add":
        print(json.dumps(add_schedule(args.date, args.time, args.event, args.duration), ensure_ascii=False))
    elif args.command == "query":
        print(json.dumps(query_schedule(args.date, args.time_range), ensure_ascii=False))
    elif args.command == "delete":
        print(json.dumps(delete_schedule(args.id), ensure_ascii=False))
    elif args.command == "update":
        print(json.dumps(update_schedule(args.id, args.time, args.event), ensure_ascii=False))
    else:
        parser.print_help()
