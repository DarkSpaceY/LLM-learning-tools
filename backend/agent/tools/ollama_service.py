import aiohttp
import json
from typing import List, Dict, Any, AsyncGenerator
from langchain.llms.base import LLM
from pydantic import BaseModel, Field


class OllamaConfig(BaseModel):
    """Ollama配置类"""
    base_url: str = Field(default="http://localhost:11434")
    model_name: str = Field(default="deepseek-r1:8b")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=1024)


class OllamaLLM(LLM):
    """Ollama LLM实现类"""
    config: OllamaConfig = Field(default_factory=OllamaConfig)

    def __init__(self, **kwargs):
        """初始化"""
        super().__init__()
        self.config = OllamaConfig(**kwargs)

    @property
    def _llm_type(self) -> str:
        """返回LLM类型"""
        return "ollama"

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
        """调用Ollama API生成文本"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.config.base_url}/api/generate"
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "model": self.config.model_name,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                }
            }
            
            print(f"发送请求: {url}")
            print(f"使用模型: {payload['model']}")

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
                    if text == "":
                        continue
                        
                    try:
                        data = json.loads(text)
                        if "error" in data:
                            raise RuntimeError(data["error"])
                        if "response" in data:
                            # 直接返回原始响应
                            response = data["response"]
                            if response != "":  # 仅用于检查非空
                                yield response  # 返回完整响应，包含换行符
                    except json.JSONDecodeError:
                        print(f"无效响应: {text[:100]}")
                        continue


class OllamaService:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    async def list_models(self) -> List[Dict[str, Any]]:
        """获取本地安装的Ollama模型列表"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/tags"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        # 格式化模型信息
                        return [
                            {
                                "id": model['name'],
                                "name": model['name'],
                                "type": "ollama",
                                "description": (
                                    f"Ollama - {model['name']}"
                                ),
                                "modified_at": model.get('modified_at', '')
                            }
                            for model in data.get('models', [])
                        ]
                    else:
                        print(
                            "Failed to get Ollama models: "
                            f"Status {response.status}"
                        )
                        return []
        except Exception as e:
            print(f"Error connecting to Ollama service: {str(e)}")
            return []

    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """获取特定模型的详细信息"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/show/{model_name}"
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(
                            "Failed to get model info: "
                            f"Status {response.status}"
                        )
                        return {}
        except Exception as e:
            print(f"Error getting model info: {str(e)}")
            return {}

    async def chat(self, model: str, messages: List[Dict[str, str]], stream: bool = False,
                   temperature: float = 0.7, max_tokens: int = 2000) -> AsyncGenerator[Dict[str, Any], None]:
        """使用Ollama模型进行对话

        Args:
            model: 模型名称
            messages: 对话历史记录列表，每条记录包含role和content字段
            stream: 是否使用流式输出
            temperature: 温度参数，控制输出的随机性
            max_tokens: 最大生成的token数量

        Returns:
            如果stream=False，返回完整的响应
            如果stream=True，返回一个异步生成器，用于流式输出
        """
        try:
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_msg = f"Chat request failed: Status {response.status}"
                        print(error_msg)
                        yield {"error": error_msg}
                        return

                    if stream:
                        async for line in response.content:
                            if line:
                                try:
                                    data = json.loads(line)
                                    yield data
                                except json.JSONDecodeError as e:
                                    print(f"Error parsing stream data: {str(e)}")
                    else:
                        data = await response.json()
                        yield data

        except Exception as e:
            error_msg = f"Error in chat: {str(e)}"
            print(error_msg)
            yield {"error": error_msg}

    async def generate(self, model: str, prompt: str, stream: bool = False,
                      temperature: float = 0.7, max_tokens: int = 2000) -> AsyncGenerator[Dict[str, Any], None]:
        """使用Ollama模型生成文本

        Args:
            model: 模型名称
            prompt: 输入提示文本
            stream: 是否使用流式输出
            temperature: 温度参数，控制输出的随机性
            max_tokens: 最大生成的token数量

        Returns:
            如果stream=False，返回完整的响应
            如果stream=True，返回一个异步生成器，用于流式输出
        """
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_msg = f"Generate request failed: Status {response.status}"
                        print(error_msg)
                        yield {"error": error_msg}
                        return

                    if stream:
                        async for line in response.content:
                            if line:
                                try:
                                    data = json.loads(line)
                                    yield data
                                except json.JSONDecodeError as e:
                                    print(f"Error parsing stream data: {str(e)}")
                    else:
                        data = await response.json()
                        yield data

        except Exception as e:
            error_msg = f"Error in generate: {str(e)}"
            print(error_msg)
            yield {"error": error_msg}


# 创建服务实例
ollama_service = OllamaService()