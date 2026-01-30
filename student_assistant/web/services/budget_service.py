import sys
from pathlib import Path

try:
    from tools import budget_cli
except ImportError:
    BASE_DIR = Path(__file__).parent.parent.parent
    sys.path.append(str(BASE_DIR))
    from tools import budget_cli

def get_monthly_summary():
    # 复用 cli 的 calculate_balance
    return budget_cli.calculate_balance()

def list_records(month=None):
    return budget_cli.list_records(month=month)["data"]

def add_record(type, amount, category, note=""):
    return budget_cli.add_record(amount, category, type, note)

def delete_record(record_id):
    return budget_cli.delete_record(record_id)

def get_stats(month=None):
    return budget_cli.get_stats(month)
