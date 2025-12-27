import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class TranslationService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未提供，请设置DEEPSEEK_API_KEY环境变量")
        
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_enhanced_prompt(self, text: str, related_terms: List[Dict[str, str]]) -> str:
        """生成增强翻译Prompt"""
        # 构建术语参考信息
        terms_info = ""
        if related_terms:
            terms_info = "\n\n相关术语参考："
            for term in related_terms:
                terms_info += f"\n- {term['term']}: {term['definition'][:100]}..."
        
        # 设计增强翻译Prompt模板
        prompt = f"""你是一位专业的翻译助手，擅长将文本准确、流畅地翻译成目标语言。

请根据以下要求翻译文本：
1. 保持原文的意思和风格
2. 注意专业术语的准确性
3. 翻译结果要自然流畅
4. 如果有相关术语参考，请结合参考信息进行翻译

{terms_info}

待翻译文本：
{text}

请输出翻译结果，不要添加任何额外的解释或说明。"""
        
        return prompt
    
    def translate(self, text: str, related_terms: List[Dict[str, str]] = None) -> str:
        """执行增强翻译"""
        if related_terms is None:
            related_terms = []
        
        # 生成增强Prompt
        prompt = self.generate_enhanced_prompt(text, related_terms)
        
        # 构建API请求体
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        try:
            # 发送API请求
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()  # 检查请求是否成功
            
            # 解析响应
            result = response.json()
            translated_text = result["choices"][0]["message"]["content"]
            
            return translated_text
        except requests.exceptions.RequestException as e:
            print(f"API调用失败: {str(e)}")
            # 返回原始文本作为降级方案
            return f"翻译失败: {str(e)}\n\n原始文本: {text}"

if __name__ == "__main__":
    # 测试翻译服务
    # 注意：需要先设置DEEPSEEK_API_KEY环境变量
    try:
        translator = TranslationService()
        
        # 测试文本
        test_text = "Artificial intelligence is transforming the world."
        
        # 测试相关术语
        related_terms = [
            {"term": "artificial intelligence", "definition": "人工智能，指由人制造出来的机器所表现出来的智能"},
            {"term": "transform", "definition": "改变，转变，使发生巨大变化"}
        ]
        
        print(f"待翻译文本: {test_text}")
        print("\n相关术语:")
        for term in related_terms:
            print(f"- {term['term']}: {term['definition']}")
        
        translated = translator.translate(test_text, related_terms)
        print(f"\n翻译结果: {translated}")
    except Exception as e:
        print(f"测试失败: {str(e)}")
