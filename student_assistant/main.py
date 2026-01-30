import sys
from pathlib import Path

# 添加项目根目录到 sys.path
BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

from config import GEMINI_API_KEY, GEMINI_MODEL, MAX_HISTORY_COUNT
from llm.gemini_client import GeminiClient
from prompts.prompt_manager import PromptManager
from agent.tool_executor import ToolExecutor
from agent.assistant import AssistantAgent

def main():
    print("正在初始化 Agent...")
    
    # 检查 API Key
    if not GEMINI_API_KEY or "your_api_key_here" in GEMINI_API_KEY:
        print("错误：未配置 GEMINI_API_KEY。请在 .env 文件中填入你的 Key。")
        return

    # 1. 初始化模块
    try:
        llm = GeminiClient(api_key=GEMINI_API_KEY, model=GEMINI_MODEL)
        prompt_manager = PromptManager()
        executor = ToolExecutor()
        
        # 2. 组装 Agent
        agent = AssistantAgent(
            llm_client=llm,
            prompt_manager=prompt_manager,
            tool_executor=executor,
            max_history=MAX_HISTORY_COUNT
        )
    except Exception as e:
        print(f"初始化失败: {e}")
        return

    print("================================================")
    print("🎓 大学生随身小秘书 (Gemini驱动)")
    print("输入 'exit' 或 'quit' 退出")
    print("================================================")

    # 3. 交互循环
    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit', '退出', '再见']:
                print("再见！")
                break
            
            response = agent.chat(user_input)
            print(f"\n小秘书: {response}")
            
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")

if __name__ == "__main__":
    main()
