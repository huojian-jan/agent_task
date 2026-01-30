import requests
import json
import time
from .base_client import BaseLLMClient

class GeminiClient(BaseLLMClient):
    """Gemini API客户端实现"""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    def chat(self, messages: list[dict], system_prompt: str = None) -> str:
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        
        # 转换消息格式为Gemini格式
        contents = []
        for msg in messages:
            # Gemini 只支持 'user' 和 'model' 角色
            role = "model" if msg["role"] == "assistant" else "user"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        payload = {"contents": contents}
        
        # Gemini的system instruction单独设置
        if system_prompt:
            payload["system_instruction"] = {
                "parts": [{"text": system_prompt}]
            }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # 安全地提取内容
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    return candidate["content"]["parts"][0]["text"]
                elif "finishReason" in candidate:
                    return f"[API返回结束原因: {candidate['finishReason']}]"
            
            return f"[API返回格式异常: {json.dumps(result)}]"
            
        except requests.exceptions.RequestException as e:
            # 简单重试或报错
            if hasattr(e.response, "text"):
                return f"API请求失败: {e.response.text}"
            return f"API请求失败: {str(e)}"
