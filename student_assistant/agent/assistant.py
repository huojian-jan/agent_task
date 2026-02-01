import json
from datetime import datetime
from typing import List, Dict

class AssistantAgent:
    """大学生小秘书Agent"""
    
    def __init__(self, llm_client, prompt_manager, tool_executor, max_history=10):
        self.llm = llm_client
        self.prompt_manager = prompt_manager
        self.executor = tool_executor
        self.max_history = max_history
        self.history: List[Dict] = []
        
    def _get_system_prompt(self) -> str:
        """获取带动态信息的system prompt"""
        template = self.prompt_manager.load("assistant")
        now = datetime.now()
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        return template.format(
            current_date=now.strftime("%Y-%m-%d"),
            current_time=now.strftime("%H:%M"),
            weekday=weekdays[now.weekday()]
        )
    
    def get_context_messages(self) -> List[Dict]:
        """获取发送给LLM的消息上下文（滑动窗口）"""
        # 始终保留 system prompt（在 Gemini Client 中处理）
        # 这里只返回 recent messages
        return self.history[-self.max_history:]
    
    def chat(self, user_input: str) -> str:
        """处理用户输入，返回回复"""
        self.history.append({"role": "user", "content": user_input})
        
        max_iterations = 8  # 防止无限循环
        
        for _ in range(max_iterations):
            # 获取上下文
            messages = self.get_context_messages()
            
            # 调用LLM
            try:
                response = self.llm.chat(
                    messages=messages,
                    system_prompt=self._get_system_prompt()
                )
            except Exception as e:
                return f"系统错误: LLM调用失败 - {str(e)}"
            
            print(f"\n[AI思考] {response[:100]}..." if len(response) > 100 else f"\n[AI思考] {response}")

            # 统一解析：final 或 tool_calls 列表
            parsed = self.executor.parse_structured_response(response)
            if parsed is None:
                # 格式错误，触发自修正
                error_msg = (
                    '系统提示：无法解析你的输出。请务必输出一个严格 JSON 对象，且包含：\n'
                    '- tool_calls：数组，每项 {"tool":"工具名","args":"参数字符串"}，可为空 []\n'
                    '- reply：字符串或 null。有最终回复时填 reply，需要调工具时填 tool_calls，二者二选一。'
                )
                print(f"[自修正] {error_msg}")
                self.history.append({"role": "assistant", "content": response})
                self.history.append({"role": "user", "content": error_msg})
                continue

            if parsed["type"] == "final":
                self.history.append({"role": "assistant", "content": response})
                return parsed["reply"]

            # parsed["type"] == "tool_calls"
            calls = parsed["calls"]
            results_parts = []
            for tool_name, args in calls:
                print(f"[调用工具] {tool_name} {args}")
                result = self.executor.execute(tool_name, args)
                print(f"[工具结果] {json.dumps(result, ensure_ascii=False)[:200]}...")
                results_parts.append(f"工具 {tool_name} 执行结果：{json.dumps(result, ensure_ascii=False)}")
            self.history.append({"role": "assistant", "content": response})
            tool_msg = "\n\n".join(results_parts)
            self.history.append({"role": "user", "content": tool_msg})
            continue

        return "抱歉，我思考了很久还是没能解决你的问题，可能是陷入了死循环。"
