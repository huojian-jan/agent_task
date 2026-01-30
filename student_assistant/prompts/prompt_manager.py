from pathlib import Path
import sys

# 适配路径
try:
    from config import PROMPTS_DIR
except ImportError:
    sys.path.append(str(Path(__file__).parent.parent))
    from config import PROMPTS_DIR

class PromptManager:
    def __init__(self, templates_dir=None):
        self.templates_dir = templates_dir or (PROMPTS_DIR / "templates")
        
    def load(self, name: str) -> str:
        """加载指定名称的prompt模板"""
        path = self.templates_dir / f"{name}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found: {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
