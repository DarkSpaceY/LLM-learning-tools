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
from .llm_providers import (
    BaseLLM,
    DeepSeekLLM,
    OpenAILLM,
    OpenRouterLLM
)
from .llm_providers import api_config, get_provider_config, get_user_settings


# 默认配置
DEFAULT_PROVIDER = api_config.default_provider
DEFAULT_MODEL = api_config.ollama["model_name"]
DEFAULT_BASE_URL = api_config.ollama["base_url"]
TIMEOUT = 60


def create_llm(provider: str = None, **kwargs) -> LLM:
    """创建LLM实例"""
    # 如果没有指定provider，从用户设置中获取
    if not provider:
        settings = get_user_settings()
        provider = settings.get("default_provider", "ollama")
    config = get_provider_config(provider)
    print(config)
    if not config and provider != "ollama":
        raise ValueError(f"未找到{provider}的配置信息")
    print(provider)
    if provider == "ollama":
        from .tools.ollama_service import OllamaLLM
        return OllamaLLM(**{**config, **kwargs})
    elif provider == "deepseek":
        return DeepSeekLLM(**{**config, **kwargs})
    elif provider == "openai":
        return OpenAILLM(**{**config, **kwargs})
    elif provider == "openrouter":
        return OpenRouterLLM(**{**config, **kwargs})
    else:
        raise ValueError(f"不支持的LLM提供商: {provider}")




class ContentGenerator:
    """内容生成器类"""

    def __init__(
        self,
        provider: str = None,
        **kwargs
    ):
        """初始化"""
        # 从用户设置中获取provider和model_name
        settings = get_user_settings()
        if not provider:
            provider = settings.get("default_provider", DEFAULT_PROVIDER)
        
        # 获取当前provider的配置
        provider_config = get_provider_config(provider)
        if provider_config and "model_name" in provider_config:
            kwargs["model_name"] = provider_config["model_name"]
            
        self.llm = create_llm(provider, **kwargs)
        # 保存LLM的配置信息
        self.config = self.llm.config

    async def process_message(
        self,
        session_id: str,
        message: str,
        model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """处理用户消息并生成内容"""
        # 使用当前加载的模型配置
        current_model = api_config.get_model_name()
        if current_model:
            self.llm.config.model_name = current_model
            print(f"使用模型: {current_model}")

        print(f"开始处理会话 {session_id} 的消息")

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