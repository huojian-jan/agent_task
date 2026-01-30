import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from config import BUDGET_FILE
except ImportError:
    sys.path.append(str(Path(__file__).parent.parent))
    from config import BUDGET_FILE

def load_data():
    if not BUDGET_FILE.exists():
        # 初始化结构
        init_data = {"monthly_budget": 1500, "category_budgets": {}, "records": []}
        save_data(init_data)
        return init_data
    
    try:
        with open(BUDGET_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"monthly_budget": 1500, "category_budgets": {}, "records": []}

def save_data(data):
    with open(BUDGET_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_record(amount, category, type="expense", note=""):
    data = load_data()
    
    new_id = 1
    if data["records"]:
        new_id = max(r["id"] for r in data["records"]) + 1
        
    record = {
        "id": new_id,
        "type": type,
        "amount": float(amount),
        "category": category,
        "note": note,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    data["records"].append(record)
    save_data(data)
    
    # 计算当前余额
    bal = calculate_balance(data)
    
    return {"success": True, "id": new_id, "message": "记录已添加", "balance": bal["balance"]}

def delete_record(record_id):
    data = load_data()
    initial_len = len(data["records"])
    data["records"] = [r for r in data["records"] if r["id"] != record_id]
    
    if len(data["records"]) == initial_len:
        return {"success": False, "message": "未找到指定ID的记录"}
        
    save_data(data)
    return {"success": True, "message": "记录已删除"}

def update_record(record_id, amount=None, note=None):
    data = load_data()
    found = False
    for r in data["records"]:
        if r["id"] == record_id:
            if amount is not None: r["amount"] = float(amount)
            if note is not None: r["note"] = note
            found = True
            break
            
    if not found:
        return {"success": False, "message": "未找到指定ID的记录"}
        
    save_data(data)
    return {"success": True, "message": "记录已更新"}

def calculate_balance(data=None):
    if data is None:
        data = load_data()
        
    # 默认只计算当月（简单起见，这里简化为计算所有记录，或者只计算当月预算剩余）
    # 逻辑：余额 = 月预算 - 当月支出 + 当月收入 (更复杂的逻辑可以后续扩展)
    # 修正逻辑：余额 = 总收入 - 总支出 (最简单的逻辑)
    # 再修正逻辑以符合大学生生活费场景：余额 = 本月预算 + 本月额外收入 - 本月支出
    
    current_month = datetime.now().strftime("%Y-%m")
    monthly_budget = data.get("monthly_budget", 1500)
    
    current_month_records = [r for r in data["records"] if r["date"].startswith(current_month)]
    
    income = sum(r["amount"] for r in current_month_records if r["type"] == "income")
    expense = sum(r["amount"] for r in current_month_records if r["type"] == "expense")
    
    # 假设 monthly_budget 是每个月固定的初始资金
    # 剩余可用 = 月预算 + 额外收入 - 支出
    balance = monthly_budget + income - expense
    
    return {
        "success": True,
        "balance": balance,
        "monthly_budget": monthly_budget,
        "monthly_income": income,
        "monthly_expense": expense
    }

def list_records(month=None, category=None, date=None):
    data = load_data()
    records = data["records"]
    
    if month:
        records = [r for r in records if r["date"].startswith(month)]
    if date:
        target_date = date
        if date == "today": target_date = datetime.now().strftime("%Y-%m-%d")
        records = [r for r in records if r["date"] == target_date]
    if category:
        records = [r for r in records if r["category"] == category]
        
    return {
        "success": True,
        "data": records,
        "count": len(records)
    }

def get_stats(month=None):
    data = load_data()
    if not month:
        month = datetime.now().strftime("%Y-%m")
        
    records = [r for r in data["records"] if r["date"].startswith(month) and r["type"] == "expense"]
    
    stats = {}
    for r in records:
        cat = r["category"]
        stats[cat] = stats.get(cat, 0) + r["amount"]
        
    return {"success": True, "month": month, "data": stats}

def set_budget(amount, category=None):
    data = load_data()
    if category:
        data["category_budgets"][category] = float(amount)
        msg = f"已设置 {category} 预算为 {amount}"
    else:
        data["monthly_budget"] = float(amount)
        msg = f"已设置月总预算为 {amount}"
        
    save_data(data)
    return {"success": True, "message": msg}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生活费管理工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # add
    add_parser = subparsers.add_parser("add", help="记账")
    add_parser.add_argument("--amount", required=True, type=float)
    add_parser.add_argument("--category", required=True)
    add_parser.add_argument("--type", choices=["income", "expense"], default="expense")
    add_parser.add_argument("--note", default="")
    
    # delete
    del_parser = subparsers.add_parser("delete", help="删除记录")
    del_parser.add_argument("--id", required=True, type=int)
    
    # update
    up_parser = subparsers.add_parser("update", help="修改记录")
    up_parser.add_argument("--id", required=True, type=int)
    up_parser.add_argument("--amount", type=float)
    up_parser.add_argument("--note")
    
    # balance
    subparsers.add_parser("balance", help="查询余额")
    
    # list
    list_parser = subparsers.add_parser("list", help="查询账单")
    list_parser.add_argument("--month", help="YYYY-MM")
    list_parser.add_argument("--date", help="YYYY-MM-DD")
    list_parser.add_argument("--category")
    
    # stats
    stats_parser = subparsers.add_parser("stats", help="统计")
    stats_parser.add_argument("--month", help="YYYY-MM")
    
    # set-budget
    budget_parser = subparsers.add_parser("set-budget", help="设置预算")
    budget_parser.add_argument("--amount", required=True, type=float)
    budget_parser.add_argument("--category")
    
    args = parser.parse_args()
    
    if args.command == "add":
        print(json.dumps(add_record(args.amount, args.category, args.type, args.note), ensure_ascii=False))
    elif args.command == "delete":
        print(json.dumps(delete_record(args.id), ensure_ascii=False))
    elif args.command == "update":
        print(json.dumps(update_record(args.id, args.amount, args.note), ensure_ascii=False))
    elif args.command == "balance":
        print(json.dumps(calculate_balance(), ensure_ascii=False))
    elif args.command == "list":
        print(json.dumps(list_records(args.month, args.category, args.date), ensure_ascii=False))
    elif args.command == "stats":
        print(json.dumps(get_stats(args.month), ensure_ascii=False))
    elif args.command == "set-budget":
        print(json.dumps(set_budget(args.amount, args.category), ensure_ascii=False))
    else:
        parser.print_help()
