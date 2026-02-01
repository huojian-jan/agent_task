import subprocess
import json
import re
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List

try:
    from config import TOOLS_DIR
except ImportError:
    sys.path.append(str(Path(__file__).parent.parent))
    from config import TOOLS_DIR

class ToolExecutor:
    """解析LLM输出的工具调用，执行CLI命令"""
    
    def __init__(self, tools_dir=None):
        self.tools_dir = tools_dir or TOOLS_DIR

    def _extract_first_json_object(self, text: str) -> Optional[Dict[str, Any]]:
        """从一段文本中尽力提取第一个“看起来像我们协议”的 JSON 对象。

        兼容模型输出前后可能夹杂的自然语言/代码块围栏等内容。
        """
        if not text:
            return None

        decoder = json.JSONDecoder()
        candidates: List[Dict[str, Any]] = []

        for m in re.finditer(r"\{", text):
            start = m.start()
            try:
                obj, _end = decoder.raw_decode(text[start:])
            except json.JSONDecodeError:
                continue

            if isinstance(obj, dict):
                # 优先返回新格式：含 tool_calls 或 reply 的统一 JSON
                if "tool_calls" in obj or "reply" in obj:
                    return obj
                # 兼容旧格式：明确带 type 的协议对象
                obj_type = obj.get("type")
                if obj_type in ("tool_call", "final"):
                    return obj
                candidates.append(obj)

        # 其次尝试“无 type 但包含关键字段”的对象
        for obj in candidates:
            if "tool" in obj and "args" in obj:
                obj.setdefault("type", "tool_call")
                return obj
            if "reply" in obj:
                obj.setdefault("type", "final")
                return obj

        return None
    
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
    
    def parse_structured_response(
        self, llm_output: str
    ) -> Optional[Dict[str, Any]]:
        """解析模型输出的统一 JSON，返回 final 或 tool_calls 列表。

        返回格式之一：
        - {"type": "final", "reply": str}
        - {"type": "tool_calls", "calls": [(tool_name, args_str), ...]}
        无法解析时返回 None。
        """
        obj = self._extract_first_json_object(llm_output)
        if not obj or not isinstance(obj, dict):
            return None

        # 新格式：tool_calls 数组
        tool_calls_raw = obj.get("tool_calls")
        if isinstance(tool_calls_raw, list) and len(tool_calls_raw) > 0:
            calls: List[Tuple[str, str]] = []
            for item in tool_calls_raw:
                if not isinstance(item, dict):
                    continue
                tool = item.get("tool")
                args = item.get("args", "")
                if isinstance(tool, str) and tool.strip():
                    if not isinstance(args, str):
                        args = json.dumps(args, ensure_ascii=False)
                    calls.append((tool.strip(), str(args).strip()))
            if calls:
                return {"type": "tool_calls", "calls": calls}

        # 新格式：reply 非空
        reply = obj.get("reply")
        if isinstance(reply, str) and reply.strip():
            return {"type": "final", "reply": reply.strip()}

        # 兼容旧格式：单条 tool_call
        if obj.get("type") == "tool_call":
            tool = obj.get("tool")
            args = obj.get("args", "")
            if isinstance(tool, str) and tool.strip():
                if not isinstance(args, str):
                    args = json.dumps(args, ensure_ascii=False)
                return {"type": "tool_calls", "calls": [(tool.strip(), str(args).strip())]}

        # 兼容旧格式：final
        if obj.get("type") == "final":
            final_reply = self.parse_reply(llm_output)
            if final_reply:
                return {"type": "final", "reply": final_reply}

        return None

    def parse_tool_call(self, llm_output: str) -> Optional[Tuple[str, str]]:
        """从LLM输出中解析工具调用
        
        期望格式:
        {"type":"tool_call","tool":"schedule","args":"query --date today"}
        """
        obj = self._extract_first_json_object(llm_output)
        if obj and obj.get("type") == "tool_call":
            tool = obj.get("tool")
            args = obj.get("args", "")
            if isinstance(tool, str) and tool.strip():
                if not isinstance(args, str):
                    args = json.dumps(args, ensure_ascii=False)
                return (tool.strip(), str(args).strip())

        # 兼容旧的 XML 格式（避免历史 prompt/测试残留导致不可用）
        tool_match = re.search(r"<tool>(.*?)</tool>", llm_output, re.DOTALL)
        args_match = re.search(r"<args>(.*?)</args>", llm_output, re.DOTALL)
        if tool_match and args_match:
            return (tool_match.group(1).strip(), args_match.group(1).strip())

        return None
    
    def parse_reply(self, llm_output: str) -> Optional[str]:
        """从LLM输出中解析最终回复"""
        obj = self._extract_first_json_object(llm_output)
        if obj and obj.get("type") == "final":
            reply = obj.get("reply")
            if isinstance(reply, str) and reply.strip():
                return reply.strip()

        # 兼容旧的 XML 格式
        reply_match = re.search(r"<reply>(.*?)</reply>", llm_output, re.DOTALL)
        if reply_match:
            return reply_match.group(1).strip()

        return None
