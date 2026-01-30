import subprocess
import json
import re
import sys
from pathlib import Path
from typing import Optional, Tuple

try:
    from config import TOOLS_DIR
except ImportError:
    sys.path.append(str(Path(__file__).parent.parent))
    from config import TOOLS_DIR

class ToolExecutor:
    """解析LLM输出的工具调用，执行CLI命令"""
    
    def __init__(self, tools_dir=None):
        self.tools_dir = tools_dir or TOOLS_DIR
    
    def execute(self, tool_name: str, args: str) -> dict:
        """执行指定工具"""
        cli_path = self.tools_dir / f"{tool_name}_cli.py"
        
        if not cli_path.exists():
            return {"success": False, "error": f"工具 {tool_name} 不存在"}
            
        cmd = f"python {cli_path} {args}"
        
        import os
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        try:
            # 使用 shell=True 来支持 Windows 下的命令执行
            result = subprocess.run(
                cmd, 
                shell=True,
                capture_output=True, 
                text=True, 
                encoding='utf-8', 
                errors='replace', # 避免编码错误导致崩溃
                env=env,
                timeout=15
            )
            
            if result.returncode != 0:
                # 尝试解析标准错误
                return {"success": False, "error": f"CLI执行错误: {result.stderr}", "raw_output": result.stdout}

            # 尝试查找输出中的 JSON 部分（防止有其他 print 干扰）
            output = result.stdout.strip()
            # 简单的提取最后一个大括号包围的内容（假设 JSON 在最后）
            json_match = re.search(r'(\{.*\})$', output, re.DOTALL)
            if json_match:
                output = json_match.group(1)
                
            return json.loads(output)
            
        except json.JSONDecodeError:
            return {"success": False, "error": "工具输出格式非标准JSON", "raw_output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def parse_tool_call(self, llm_output: str) -> Optional[Tuple[str, str]]:
        """从LLM输出中解析工具调用
        
        期望格式:
        <tool>schedule</tool>
        <args>query --date today</args>
        """
        tool_match = re.search(r'<tool>(.*?)</tool>', llm_output, re.DOTALL)
        args_match = re.search(r'<args>(.*?)</args>', llm_output, re.DOTALL)
        
        if tool_match and args_match:
            return (tool_match.group(1).strip(), args_match.group(1).strip())
        return None
    
    def parse_reply(self, llm_output: str) -> Optional[str]:
        """从LLM输出中解析最终回复"""
        reply_match = re.search(r'<reply>(.*?)</reply>', llm_output, re.DOTALL)
        if reply_match:
            return reply_match.group(1).strip()
        return None
