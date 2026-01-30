class BaseLLMClient:
    """LLM客户端基类，定义统一接口"""
    def chat(self, messages: list[dict], system_prompt: str = None) -> str:
        """发送消息并获取回复
        
        Args:
            messages: 对话历史，格式 [{"role": "user/assistant", "content": "..."}]
            system_prompt: 系统提示词
            
        Returns:
            str: LLM的回复内容
        """
        raise NotImplementedError
