"""
AI教育助手agent模块

提供了基于LangChain的智能代理系统，集成了：
- 本地Ollama模型支持
- 工具调用能力
- 会话管理
- 错误处理
"""

from .tools.ollama_service import OllamaLLM
from .langchain_agent import (
    ContentGenerator,
    langchain_agent
)

from .tools import (
    Exercise,
    ExerciseSet,
    ExerciseGenerator,
    Resource,
    ResourceList,
    KnowledgeSearcher,
    search_resources,
    KnowledgeNode,
    KnowledgeEdge,
    KnowledgeGraphGenerator,
    SimulationBuilder,
    generate_section_content
)

__all__ = [
    # Agent类
    'OllamaLLM',
    'ContentGenerator',
    'langchain_agent',
    
    # 工具类
    'Exercise',
    'ExerciseSet',
    'ExerciseGenerator',
    'Resource',
    'ResourceList',
    'KnowledgeSearcher',
    'search_resources',
    'KnowledgeNode',
    'KnowledgeEdge',
    'KnowledgeGraphGenerator',
    'SimulationBuilder',
    'generate_section_content'
]

# 版本信息
__version__ = '0.1.0'
__author__ = 'AI Education Team'
__description__ = 'LangChain based AI agent for education'

# 默认配置
DEFAULT_MODEL = "deepseek-r1:8b"
DEFAULT_BASE_URL = "http://localhost:11434"
MAX_RETRIES = 3
TIMEOUT = 30