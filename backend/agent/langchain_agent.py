from typing import Dict, Any, Optional, AsyncGenerator, TYPE_CHECKING, List
from dataclasses import dataclass, field
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests
import re

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
import os,sys

# 默认配置
DEFAULT_PROVIDER = api_config.default_provider
DEFAULT_MODEL = api_config.ollama["model_name"]
DEFAULT_BASE_URL = api_config.ollama["base_url"]
TIMEOUT = 60

@dataclass
class Chapter:
    """章节数据结构"""
    number: int
    title: str
    description: str
    sections: List['Section'] = field(default_factory=list)


@dataclass
class Section:
    """小节数据结构"""
    number: str  # 如 "1.1"
    title: str
    description: str
    content: str = ""

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
        # 初始化临时JSON存储
        self.temp_json = {
            "chapters": []
        }
        # 初始化生成状态
        self.generating = False
        # 初始化会话状态字典
        self.session_states = {}

    def stop_generation(self, session_id: str) -> bool:
        """停止指定会话的生成过程"""
        if session_id in self.session_states:
            self.session_states[session_id] = False
            return True
        return False

    def format_json_to_text(self, data: dict) -> str:
        """将JSON数据转换为自然语言描述"""
        text = []
        if 'chapters' in data:
            for idx, chapter in enumerate(data.get('chapters', []), 1):
                text.append(f"{chapter.get('title', '')}")

                if 'sections' in chapter:
                    for idy, section in enumerate(chapter.get('sections', []), 1):
                        text.append(f"• {section.get('title', '')}")
        return '\n'.join(text)

    async def web_search(self, query: str, max_results: int = 1, lang: str = 'zh') -> str:
        import time, json, requests
        print(f"开始网络搜索，查询词: {query}, 最大结果数: {max_results}, 语言: {lang}")
        # 1. 初始化API参数和headers
        base_url = f"https://{lang}.wikipedia.org/w/api.php"
        headers = {"User-Agent": "MyWikipediaBot/1.0 (contact@example.com)"}
        print(f"使用API地址: {base_url}")
        
        # 2. 获取相关页面标题
        def get_titles():
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": max_results,
                "srprop": "",
            }
            print("正在获取相关页面标题...")
            response = requests.get(base_url, params=params, headers=headers)
            data = response.json()
            titles = [item["title"] for item in data["query"]["search"][:max_results]]
            print(f"获取到{len(titles)}个相关标题")
            return titles
        
        # 3. 获取单个页面完整内容
        def get_page_content(title: str) -> Dict[str, str]:
            print(f"\n正在获取页面内容: {title}")
            # 先获取摘要
            params_intro = {
                "action": "query",
                "format": "json",
                "titles": title,
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "redirects": True,
            }
            
            # 再获取全文（分页处理）
            print("开始获取完整内容...")
            full_text = ""
            continue_params = {}
            page_count = 0
            while True:
                page_count += 1
                print(f"正在获取第{page_count}页内容...")
                params_full = {
                    "action": "query",
                    "format": "json",
                    "titles": title,
                    "prop": "extracts",
                    "explaintext": True,
                    "exintro": False,
                    **continue_params
                }
                response = requests.get(base_url, params=params_full, headers=headers)
                data = response.json()
                page = next(iter(data["query"]["pages"].values()))
                if "extract" in page:
                    full_text += page["extract"]
                if "continue" not in data:
                    break
                continue_params = data["continue"]
                time.sleep(0.2)  # 避免触发速率限制
            
            print("获取摘要...")
            # 获取摘要
            response_intro = requests.get(base_url, params=params_intro, headers=headers)
            intro_data = response_intro.json()
            intro_page = next(iter(intro_data["query"]["pages"].values()))
            summary = intro_page.get("extract", "")[:500]  # 摘要限500字
            
            print(f"页面 '{title}' 内容获取完成")
            return {
                "title": title,
                "summary": summary,
                "content": full_text.strip()
            }
        
        # 主流程
        try:
            print("\n开始执行主要搜索流程...")
            titles = get_titles()
            results = []
            for i, title in enumerate(titles, 1):
                print(f"\n处理第{i}/{len(titles)}个标题...")
                time.sleep(0.5)  # 请求间隔
                results.append(get_page_content(title))
            print(f"搜索完成，共获取{len(results)}个结果")
            return str(results)
        
        except Exception as e:
            print(f"Error fetching Wikipedia pages: {e}")
            print("搜索过程出现错误，返回空结果")
            return "[]"


    async def process_message(
        self,
        session_id: str,
        message: str,
        model: Optional[str] = None,
        has_outline: bool = False,
        tutorial_data: Optional[dict] = None,
        use_web_search: bool = False,
    ) -> AsyncGenerator[str, None]:
        """处理用户消息并生成内容"""
        # 使用当前加载的模型配置
        current_model = api_config.get_model_name()
        if current_model:
            self.llm.config.model_name = current_model
            print(f"使用模型: {current_model}")

        print(f"开始处理会话 {session_id} 的消息")
        
        # 初始化会话状态
        self.session_states[session_id] = True

        # 开始渐进式生成
        try:
            # 如果没有现有大纲，则生成主要章节和小节
            if not has_outline:
                # 1. 生成主要章节
                print("开始生成主要章节...")
                yield {
                    "type": "progress",
                    "stage": "chapters",
                    "status": "start"
                }

                chapters: List['Chapter'] = []
                chapter_count = 0
                
                # 清空临时JSON存储
                self.temp_json = {
                    "chapters": [],
                }

                web_context = ""
                if use_web_search:
                    yield {
                        "type": "info",
                        "message": f"正在搜索主题: '{message}'..."
                    }
                    web_context = await self.web_search(message)
                    if web_context:
                        yield {
                            "type": "info",
                            "message": "已获取网络参考信息"
                        }
                
                async for data in generate_main_outline(message, self.llm, web_context=web_context):
                    # 检查是否需要停止生成
                    if not self.session_states.get(session_id, True):
                        yield {
                            "type": "stopped",
                            "message": "生成已停止"
                        }
                        return
                        
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
                                # 更新临时JSON
                                self.temp_json["chapters"].append({
                                    "number": chapter.number,
                                    "title": chapter.title,
                                    "description": chapter.description,
                                    "sections": []
                                })
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
            else:
                # 如果有现有大纲，直接开始生成内容
                print("\n开始生成缺失的小节内容...")
                self.temp_json = {
                    "chapters": [],
                }
                chapters = []
                for i in tutorial_data["chapters"]:
                    chapter = Chapter(
                        number=i["number"],
                        title=i["title"],
                        description=i["description"],
                        sections=[Section(number=s["number"], title=s["title"], description=s["description"], content=s["content"]) for s in i["sections"]]
                    )
                    chapters.append(chapter)
                    self.temp_json["chapters"].append({
                        "number": chapter.number,
                        "title": chapter.title,
                        "description": chapter.description,
                        "sections": [{"number":i.number,"title":i.title,"description":i.description,"content":i.content} for i in chapter.sections]
                    })
                yield {
                    "type": "progress",
                    "stage": "content",
                    "status": "start"
                }

            section_count = 0
            for chapter in chapters:
                    if chapter.sections == []:
                        print(f"\n处理章节: {chapter.title}")
                        # 将临时JSON格式化并传递给LLM
                        context_text = self.format_json_to_text(self.temp_json)

                        chapter_web_context = ""
                        if use_web_search:
                            yield {
                                "type": "info",
                                "message": f"正在搜索章节: '{chapter.title}'..."
                            }
                            chapter_web_context = await self.web_search(chapter.title)
                            if chapter_web_context:
                                yield {
                                    "type": "info",
                                    "message": "已获取网络参考信息"
                                }

                        async for data in generate_chapter_outline(message, chapter, self.llm, context=context_text, web_context=chapter_web_context):
                            # 检查是否需要停止生成
                            if not self.session_states.get(session_id, True):
                                yield {
                                    "type": "stopped",
                                    "message": "生成已停止"
                                }
                                return
                                
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
                                        # 更新临时JSON
                                        for ch in self.temp_json["chapters"]:
                                            if ch["number"] == chapter.number:
                                                ch["sections"].append({
                                                    "number": section.number,
                                                    "title": section.title,
                                                    "description": section.description,
                                                    "content": ""
                                                })
                                        yield {
                                            "type": "section",
                                            "data": {
                                                "chapter": chapter.number,
                                                "number": section.number,
                                                "title": section.title,
                                                "description": section.description
                                            }
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
                    # 检查小节内容是否已生成
                    if not section.content or section.content == "":
                        print(f"\n生成内容: {section.title}")
                        section_content = []
                        
                        # 将临时JSON格式化并传递给LLM
                        context_text = self.format_json_to_text(self.temp_json)

                        section_web_context = ""
                        if use_web_search:
                            yield {
                                "type": "info",
                                "message": f"正在搜索小节: '{section.title}'..."
                            }
                            section_web_context = await self.web_search(section.title)
                            if section_web_context:
                                yield {
                                    "type": "info",
                                    "message": "已获取网络参考信息"
                                }

                        async for data in generate_section_content(message, section, self.llm, context=context_text, web_context=section_web_context):
                            # 检查是否需要停止生成
                            if not self.session_states.get(session_id, True):
                                yield {
                                    "type": "stopped",
                                    "message": "生成已停止"
                                }
                                return
                                
                            if isinstance(data, dict):
                                if data['type'] == "chunk":
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
                    content_count += 1

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
            tb = getattr(e, '__traceback__', None)
            if tb is not None:
                # 提取文件名（仅显示基本名称）和行号
                filename = os.path.basename(tb.tb_frame.f_code.co_filename)
                lineno = tb.tb_lineno
                location = f"文件: {filename}, 行号: {lineno}"
            else:
                location = "位置未知"
        
            print(f"\n错误：{error}\n发生位置：{location}")
            yield {
                "type": "error",
                "message": f"生成过程出错: {error} ({location})"
            }


# 创建代理实例
langchain_agent = ContentGenerator()