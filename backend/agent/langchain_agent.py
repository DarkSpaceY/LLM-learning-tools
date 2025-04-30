from typing import Dict, Any, Optional, AsyncGenerator, TYPE_CHECKING, List

if TYPE_CHECKING:
    from .tools.content_generator import Chapter, Section
import json
import asyncio
import aiohttp
from langchain.llms.base import LLM
from pydantic import Field
from pydantic_settings import BaseSettings
from .tools.content_generator import (
    generate_main_outline,
    generate_chapter_outline,
    generate_section_content
)


class OllamaConfig(BaseSettings):
    """Ollama配置"""
    model_name: str = Field(
        default="deepseek-r1:8b",
        description="Ollama模型名称"
    )
    base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API基础URL"
    )
    temperature: float = Field(
        default=0.7,
        description="生成温度",
        ge=0.0,
        le=1.0
    )
    max_tokens: int = Field(
        default=1024,
        description="最大生成长度",
        gt=0
    )


class OllamaLLM(LLM):
    """自定义Ollama LLM类"""
    
    config: OllamaConfig = Field(default_factory=OllamaConfig)
    
    def __init__(
        self,
        model_name: str = "deepseek-r1:8b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        max_tokens: int = 1024
    ):
        """初始化"""
        config = OllamaConfig(
            model_name=model_name,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens
        )
        super().__init__(config=config)

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
        """调用Ollama API生成文本，支持流式输出"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.config.base_url}/api/generate"
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "model": self.config.model_name,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": self.config.temperature,
                    # "num_predict": self.config.max_tokens,
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


class ContentGenerator:
    """内容生成器类"""

    def __init__(
        self,
        model_name: str = "deepseek-r1:8b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        max_tokens: int = 1024
    ):
        """初始化"""
        self.llm = OllamaLLM(
            model_name=model_name,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens
        )

    async def process_message(
        self,
        session_id: str,
        message: str,
        model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """处理用户消息并生成内容"""
        # 如果指定了模型，更新LLM配置
        if model:
            self.llm.config.model_name = model
            print(f"使用模型: {model}")

        print(f"开始处理会话 {session_id} 的消息")

        # 检查Ollama服务是否可用
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        f"{self.llm.config.base_url}/api/version",
                        timeout=5
                    ) as response:
                        if response.status != 200:
                            try:
                                error_body = await response.json()
                                error_msg = error_body.get(
                                    'error', '服务响应异常'
                                )
                            except (json.JSONDecodeError, aiohttp.ClientError):
                                error_msg = (
                                    await response.text() or 
                                    f"HTTP {response.status}"
                                )
                            raise RuntimeError(f"Ollama异常: {error_msg}")
                            
                        version_info = await response.json()
                        version = version_info.get('version', 'unknown')
                        print(f"Ollama版本: {version}")
                except aiohttp.ClientError as e:
                    raise RuntimeError(f"无法连接Ollama: {e}")
                except asyncio.TimeoutError:
                    raise RuntimeError("连接Ollama超时")
                    
        except Exception as e:
            error = str(e)
            print(f"\n错误：{error}")
            yield "\n❌ Ollama服务检查失败"
            if "无法连接" in error or "超时" in error:
                yield "\n💡 提示：请检查服务是否已启动"
            elif "异常" in error:
                yield "\n💡 提示：服务可能需要重启"
            return

        # 开始渐进式生成
        try:
            # 1. 生成主要章节
            print("开始生成主要章节...")
            yield {
                "type": "progress",
                "stage": "chapters",
                "status": "start"
            }

            chapters: List['Chapter'] = []
            chapter_count = 0
            
            async for data in generate_main_outline(message, self.llm):
                if isinstance(data, dict):
                    if data['type'] == "chunk":
                        yield {
                            "type": "chunk",
                            "content": data["data"]
                        }
                    elif data['type'] == "chapters":
                        for chapter in data["data"]:
                            chapter_count += 1
                            chapters.append(chapter)
                            yield {
                                "type": "chapter",
                                "data": {
                                    "number": chapter.number,
                                    "title": chapter.title,
                                    "description": chapter.description
                                }
                            }

            if not chapters:
                yield {
                    "type": "error",
                    "message": "生成章节失败"
                }
                return

            yield {
                "type": "progress",
                "stage": "chapters",
                "status": "complete",
                "count": chapter_count
            }

            # 2. 生成小节
            print("\n开始生成小节...")
            yield {
                "type": "progress",
                "stage": "sections",
                "status": "start"
            }

            section_count = 0
            for chapter in chapters:
                print(f"\n处理章节: {chapter.title}")
                chapter.sections = []

                async for data in generate_chapter_outline(message, chapter, self.llm):
                    if isinstance(data, dict):
                        if data['type'] == "chunk":
                            yield {
                                "type": "chunk",
                                "content": data["data"]
                            }
                        elif data['type'] == "sections":
                            for section in data["data"]:
                                section_count += 1
                                chapter.sections.append(section)
                                yield {
                                    "type": "section",
                                    "data": {
                                        "chapter": chapter.number,
                                        "number": section.number,
                                        "title": section.title,
                                        "description": section.description
                                    }
                                }

            yield {
                "type": "progress",
                "stage": "sections",
                "status": "complete",
                "count": section_count
            }

            # 3. 生成详细内容
            print("\n开始生成详细内容...")
            yield {
                "type": "progress",
                "stage": "content",
                "status": "start"
            }

            content_count = 0
            for chapter in chapters:
                for section in chapter.sections:
                    print(f"\n生成内容: {section.title}")
                    section_content = []
                    
                    async for data in generate_section_content(message, section, self.llm):
                        if isinstance(data, dict):
                            if data['type'] == "chunk":
                                content_count += 1
                                # 发送chunk到前端
                                yield {
                                    "type": "chunk",
                                    "content": data["data"]
                                }
                                section_content.append(data["data"])
                            elif data['type'] == "content":
                                # 完成一个小节的内容生成后发送完整内容
                                full_content = data["data"]
                                section.content = full_content
                                yield {
                                    "type": "content",
                                    "data": {
                                        "chapter": chapter.number,
                                        "section": section.number,
                                        "content": full_content
                                    }
                                }

            yield {
                "type": "progress",
                "stage": "content",
                "status": "complete",
                "count": content_count
            }

            print("\n内容生成完成！")
            yield {
                "type": "complete",
                "message": "内容生成完成"
            }

        except Exception as e:
            error = str(e) or "未知错误"
            print(f"\n错误：{error}")
            yield {
                "type": "error",
                "message": f"生成过程出错: {error}"
            }


# 创建代理实例
langchain_agent = ContentGenerator()