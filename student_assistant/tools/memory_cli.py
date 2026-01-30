import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from config import MEMORY_FILE
except ImportError:
    sys.path.append(str(Path(__file__).parent.parent))
    from config import MEMORY_FILE

def load_data():
    if not MEMORY_FILE.exists():
        return []
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_data(data):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_memory(role, content):
    data = load_data()
    
    new_id = 1
    if data:
        new_id = max(item['id'] for item in data) + 1
        
    new_item = {
        "id": new_id,
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    data.append(new_item)
    save_data(data)
    return {"success": True, "message": "已保存记忆"}

def query_memory(keyword):
    data = load_data()
    if not keyword:
        return {"success": False, "message": "关键词不能为空"}
        
    # 简单关键词匹配
    results = [item for item in data if keyword in item['content']]
    
    # 按时间倒序
    results.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return {"success": True, "data": results[:5]} # 最多返回5条

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="记忆检索工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # query
    query_parser = subparsers.add_parser("query", help="查询记忆")
    query_parser.add_argument("--keyword", required=True)
    
    # save
    save_parser = subparsers.add_parser("save", help="保存记忆")
    save_parser.add_argument("--role", required=True, choices=["user", "assistant"])
    save_parser.add_argument("--content", required=True)
    
    args = parser.parse_args()
    
    if args.command == "query":
        print(json.dumps(query_memory(args.keyword), ensure_ascii=False))
    elif args.command == "save":
        print(json.dumps(save_memory(args.role, args.content), ensure_ascii=False))
    else:
        parser.print_help()
