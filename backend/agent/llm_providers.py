from typing import Dict, Any, Optional, AsyncGenerator
import json
import aiohttp
import os
from langchain.llms.base import LLM
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings

def get_user_settings() -> dict:
    """获取用户设置"""
    settings_path = os.path.join(os.path.dirname(__file__), "../settings/user_settings.json")
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
            global_settings = settings.get("global", {})
            # 从global字段中提取提供商配置
            provider_settings = {}
            for provider in ["ollama", "deepseek", "openai", "openrouter"]:
                if provider in global_settings:
                    provider_settings[provider] = global_settings[provider]
            # 添加default_provider
            if "default_provider" in global_settings:
                provider_settings["default_provider"] = global_settings["default_provider"]
            return provider_settings
    except Exception as e:
        print(f"读取用户设置失败: {str(e)}")
        return {}

class BaseLLMConfig(BaseModel):
    """基础LLM配置"""
    base_url: str
    model_name: str
    temperature: float = 0.7
    max_tokens: Optional[int] = Field(default=1024, gt=-2)

class LLMProviderConfig(BaseLLMConfig):
    """LLM提供商配置"""
    api_key: str
    provider: str

class APIConfig(BaseSettings):
    """API配置管理"""
    # 默认LLM提供商
    default_provider: str = "ollama"
    
    # Ollama配置
    ollama: Dict[str, Any] = {
        "base_url": "http://localhost:11434",
        "model_name": "deepseek-r1:8b",
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    # DeepSeek配置
    deepseek: Optional[LLMProviderConfig] = None
    
    # OpenAI配置
    openai: Optional[LLMProviderConfig] = None
    
    # OpenRouter配置
    openrouter: Optional[LLMProviderConfig] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 从用户设置中加载配置
        settings = get_user_settings()
        if settings:
            # 更新默认提供商
            if "default_provider" in settings:
                self.default_provider = settings["default_provider"]
                
            # 更新提供商配置
            for provider in ["ollama", "deepseek", "openai", "openrouter"]:
                if provider in settings:
                    config = settings[provider].copy()  # 创建配置的副本
                    # 删除models字段
                    if "models" in config:
                        del config["models"]
                    if provider == "ollama":
                        # 确保ollama配置包含所有必要字段
                        self.ollama.update({
                            "base_url": config.get("base_url", self.ollama["base_url"]),
                            "model_name": config.get("model_name", self.ollama["model_name"]),
                            "temperature": config.get("temperature", self.ollama["temperature"]),
                            "max_tokens": config.get("max_tokens", self.ollama["max_tokens"])
                        })
                    else:
                        # 确保非ollama提供商配置包含所有必要字段
                        config["provider"] = provider
                        if "api_key" not in config:
                            config["api_key"] = ""
                        setattr(self, provider, LLMProviderConfig(**config))
                        
    def get_model_name(self) -> str:
        """根据default_provider获取对应提供商的model_name"""
        if self.default_provider == "ollama":
            return self.ollama["model_name"]
        provider_config = getattr(self, self.default_provider)
        return provider_config.model_name if provider_config else None

# 全局配置实例
api_config = APIConfig()

def update_provider_config(provider: str, config: Dict[str, Any]) -> None:
    """更新提供商配置"""
    if provider not in ["ollama", "deepseek", "openai", "openrouter"]:
        raise ValueError(f"不支持的LLM提供商: {provider}")
        
    if provider == "ollama":
        api_config.ollama.update(config)
    else:
        config['provider'] = provider  # Add provider field
        setattr(api_config, provider, LLMProviderConfig(**config))

def get_provider_config(provider: str) -> Dict[str, Any]:
    """获取提供商配置"""
    if provider not in ["ollama", "deepseek", "openai", "openrouter"]:
        raise ValueError(f"不支持的LLM提供商: {provider}")
    
    # 获取用户设置
    settings = get_user_settings()
    provider_settings = settings.get("providers", {})
    
    # 优先使用用户设置中的配置
    if provider in provider_settings:
        return provider_settings[provider]
    
    if provider == "ollama":
        return api_config.ollama
    else:
        config = getattr(api_config, provider)
        return config.dict() if config else None

class BaseLLM(LLM):
    """基础LLM实现"""
    config: BaseLLMConfig

    @property
    def _llm_type(self) -> str:
        """返回LLM类型"""
        raise NotImplementedError

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """返回标识参数"""
        return {
            "model_name": self.config.model_name,
            "base_url": self.config.base_url,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }

    async def _call(
        self,
        prompt: str,
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """调用API生成文本"""
        async with aiohttp.ClientSession() as session:
            # 根据不同提供商设置不同的API路径
            if isinstance(self, OpenAILLM):
                url = f"{self.config.base_url}/responses"
            else:
                url = f"{self.config.base_url}/chat/completions"
                
            headers = self._get_headers()
            payload = self._get_payload(prompt)

            async with session.post(
                url,
                json=payload,
                headers=headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(
                        f"API错误 ({response.status}): {error_text}"
                    )

                async for line in response.content:
                    if not line:
                        continue
                        
                    text = line.decode('utf-8')
                    if text.startswith('data: '):
                        text = text[6:]
                    if text == "[DONE]":
                        break
                        
                    try:
                        data = json.loads(text)
                        if "error" in data:
                            raise RuntimeError(data["error"])
                            
                        # 根据不同提供商处理不同的响应格式
                        if isinstance(self, OpenAILLM):
                            if "text" in data:
                                yield data["text"]
                        else:
                            if "choices" in data and len(data["choices"]) > 0:
                                content = data["choices"][0].get("delta", {}).get("content")
                                if content:
                                    yield content
                    except json.JSONDecodeError:
                        continue

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }

    def _get_payload(self, prompt: str) -> Dict[str, Any]:
        """获取请求负载"""
        # 根据不同提供商设置不同的请求格式
        if isinstance(self, OpenAILLM):
            payload = {
                "model": self.config.model_name,
                "input": prompt,
                "temperature": self.config.temperature
            }
        else:
            payload = {
                "model": self.config.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
                "temperature": self.config.temperature
            }
        
        # 只有当max_tokens不为-1时才添加该参数
        if self.config.max_tokens != -1:
            payload["max_tokens"] = self.config.max_tokens
            
        return payload

class DeepSeekLLM(BaseLLM):
    """DeepSeek LLM实现"""
    config: LLMProviderConfig = Field(default_factory=lambda: api_config.deepseek or LLMProviderConfig(
        api_key="",
        base_url="https://api.deepseek.com",
        model_name="deepseek-chat",  # DeepSeek-V3模型
        provider="deepseek",
        temperature=0.7,
        max_tokens=1024
    ))

    @property
    def _llm_type(self) -> str:
        return "deepseek"

    def _get_headers(self) -> Dict[str, str]:
        print("Getting headers for DeepSeekLLM", self.config.api_key)
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }

class OpenAILLM(BaseLLM):
    """OpenAI LLM实现"""
    config: LLMProviderConfig = Field(default_factory=lambda: api_config.openai or LLMProviderConfig(
        api_key="",
        base_url="https://api.openai.com/v1",
        model_name="gpt-3.5-turbo",
        provider="openai",
        temperature=0.7,
        max_tokens=1024
    ))

    @property
    def _llm_type(self) -> str:
        return "openai"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }

class OpenRouterLLM(BaseLLM):
    """OpenRouter LLM实现"""
    config: LLMProviderConfig = Field(default_factory=lambda: api_config.openrouter or LLMProviderConfig(
        api_key="",
        base_url="https://openrouter.ai/api/v1",
        model_name="openai/gpt-3.5-turbo",
        provider="openrouter",
        temperature=0.7,
        max_tokens=1024
    ))

    @property
    def _llm_type(self) -> str:
        return "openrouter"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "HTTP-Referer": "https://github.com/OpenRouterTeam/openrouter-python",
            "X-Title": "AI Education Backend"
        }