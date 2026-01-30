# 大学生随身小秘书 Agent (Student Assistant Agent)

这是一个基于 LLM (Gemini) 的智能 Agent 学习项目，旨在帮助大学生管理日常学习和生活。

## 🌟 核心功能

-   **📅 日程管理**: 增删改查日常安排，支持自然语言冲突检测。
-   **📚 课程查询**: 随时查询课表，精确到教室和时间。
-   **💰 财务管家**: 记录收支、查询余额、生成消费统计，设置月度预算。
-   **🌤️ 天气预报**: 获取目标日期的天气情况及穿衣/出行建议。
-   **🧠 长期记忆**: Agent 会自动记录对话，并能通过 `memory_cli` 检索之前的关键信息。
-   **🤖 智能对话**: 热情、话痨的性格，支持多轮对话、滑动窗口记忆及自修正能力。
-   **🌐 Web 管理后台**: 直观管理所有数据，与 Agent 实时同步。

## 🛠️ 技术架构

-   **LLM**: Google Gemini API (Planner 角色)
-   **Agent 模式**: ReAct (Reasoning + Acting)
-   **后端**: Python 3.10+, FastAPI (Web 后端)
-   **工具层**: 独立 CLI 脚本 (`subprocess` 调用)
-   **数据持久化**: 本地 JSON 文件
-   **前端**: Jinja2 + Tailwind CSS

## 📂 项目结构

```text
student_assistant/
├── agent/              # Agent 核心逻辑 (执行器、大脑)
├── tools/              # 5 大 CLI 工具 (Schedule, Course, Budget, Weather, Memory)
├── llm/                # LLM 客户端适配器
├── prompts/            # 系统提示词模板
├── web/                # FastAPI Web 后台
│   ├── routers/        # 业务路由
│   ├── services/       # 数据服务层
│   └── templates/      # HTML 模板
├── eval/               # 评估系统 (测试用例、评估器)
├── data/               # 数据存储 (JSON)
├── main.py             # Agent 命令行入口
└── config.py           # 全局配置
```

## 🚀 快速开始

1.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **配置环境**:
    编辑 `.env` 文件，填入你的 Gemini API Key：
    ```text
    GEMINI_API_KEY=your_actual_key
    GEMINI_MODEL=gemini-1.5-flash
    MAX_HISTORY_COUNT=10
    ```

3.  **启动 Agent (命令行)**:
    ```bash
    python main.py
    ```

4.  **启动 Web 后台**:
    ```bash
    python -m uvicorn web.app:app --reload --port 8000
    ```
    访问: `http://localhost:8000`

5.  **运行评估**:
    ```bash
    python eval/evaluator.py
    ```

## 📈 评估指标

-   **意图识别准确率**: LLM 是否选择了正确的工具。
-   **参数提取准确率**: 日期、时间、金额等参数是否提取正确。
-   **执行成功率**: CLI 工具返回结果的成功率。
-   **自修正触发次数**: Agent 在格式错误时自我纠正的能力。

## ⚠️ 注意事项

-   本项目的 CLI 和 Web 端共享 JSON 文件，并发写入可能会导致小概率冲突（实验性项目未加锁）。
-   请确保已安装 Python 并配置好环境变量。
