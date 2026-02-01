import os
import json
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.assistant import AssistantAgent
from llm.gemini_client import GeminiClient
from prompts.prompt_manager import PromptManager
from agent.tool_executor import ToolExecutor
import config

class Evaluator:
    def __init__(self, test_cases_path):
        self.test_cases = self.load_test_cases(test_cases_path)
        
        # 初始化 Agent
        llm = GeminiClient(api_key=config.GEMINI_API_KEY, model=config.GEMINI_MODEL)
        pm = PromptManager()
        executor = ToolExecutor()
        self.agent = AssistantAgent(llm, pm, executor, max_history=5)
        
    def load_test_cases(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def run(self):
        results = []
        print(f"开始评估，共 {len(self.test_cases)} 个测试用例...\n")
        
        for case in self.test_cases:
            print(f"正在运行测试用例 {case['id']}: {case['name']}...")
            print(f"输入: {case['query']}")
            
            try:
                # 记录开始时间
                start_time = datetime.now()
                
                # 执行对话
                # 注意：为了评估准确性，我们可能需要拦截 tool_executor 的调用
                # 或者通过分析 history 来判断
                self.agent.chat(case['query'])
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # 评估指标
                metrics = {
                    "id": case['id'],
                    "name": case['name'],
                    "success": False,
                    "tool_match": False,
                    "params_match": False,
                    "duration": duration,
                    "error": None
                }
                
                # 检查是否调用了工具（支持新格式：tool_calls 列表）
                tool_call_content = None
                matched_tool_name = None
                matched_tool_args = None
                for msg in reversed(self.agent.history):
                    if msg["role"] != "assistant":
                        continue
                    content = msg.get("content", "")
                    parsed = self.agent.executor.parse_structured_response(content)
                    if parsed and parsed.get("type") == "tool_calls":
                        for tool_name, tool_args in parsed.get("calls", []):
                            if case["expected_tool"].lower() in (tool_name or "").lower():
                                matched_tool_name = tool_name
                                matched_tool_args = tool_args
                                tool_call_content = content
                                break
                        if tool_call_content:
                            break
                    # 兼容旧格式：单条 tool_call
                    if not tool_call_content:
                        single = self.agent.executor.parse_tool_call(content)
                        if single:
                            matched_tool_name, matched_tool_args = single
                            tool_call_content = content
                            break
                
                if tool_call_content:
                    if (matched_tool_name and case["expected_tool"].lower() in matched_tool_name.lower()) or (
                        case["expected_tool"].lower() in tool_call_content.lower()
                    ):
                        metrics["tool_match"] = True
                    all_params_found = True
                    for param in case.get('expected_params', []):
                        haystack = matched_tool_args or tool_call_content
                        if param not in haystack:
                            all_params_found = False
                            break
                    metrics["params_match"] = all_params_found
                
                # 综合判断成功
                if metrics["tool_match"] and metrics["params_match"]:
                    metrics["success"] = True
                
                results.append(metrics)
                print(f"结果: {'✅' if metrics['success'] else '❌'} (耗时: {duration:.2f}s)\n")
                
            except Exception as e:
                print(f"运行失败: {str(e)}\n")
                results.append({
                    "id": case['id'],
                    "name": case['name'],
                    "success": False,
                    "error": str(e)
                })
                
        return results

    def print_summary(self, results):
        total = len(results)
        success = sum(1 for r in results if r.get('success'))
        
        print("="*30)
        print("评估结果摘要")
        print("="*30)
        print(f"总计: {total}")
        print(f"成功: {success}")
        print(f"失败: {total - success}")
        print(f"成功率: {(success/total*100):.2f}%")
        print("="*30)

if __name__ == "__main__":
    test_cases_file = os.path.join(os.path.dirname(__file__), "test_cases.json")
    evaluator = Evaluator(test_cases_file)
    results = evaluator.run()
    evaluator.print_summary(results)
