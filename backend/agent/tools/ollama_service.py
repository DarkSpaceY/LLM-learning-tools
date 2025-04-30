import aiohttp
from typing import List, Dict, Any


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


# 创建服务实例
ollama_service = OllamaService()