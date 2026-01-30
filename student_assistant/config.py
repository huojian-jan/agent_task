import os
from dotenv import load_dotenv
from pathlib import Path

# 加载 .env 文件
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path, override=True)

# 基础配置
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TOOLS_DIR = BASE_DIR / "tools"
PROMPTS_DIR = BASE_DIR / "prompts"

# 确保数据目录存在
DATA_DIR.mkdir(exist_ok=True)

# LLM 配置
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
MAX_HISTORY_COUNT = int(os.getenv("MAX_HISTORY_COUNT", "10"))

# 数据文件路径
SCHEDULE_FILE = DATA_DIR / "schedule.json"
COURSE_FILE = DATA_DIR / "courses.json"
BUDGET_FILE = DATA_DIR / "budget.json"
MEMORY_FILE = DATA_DIR / "memory.json"
