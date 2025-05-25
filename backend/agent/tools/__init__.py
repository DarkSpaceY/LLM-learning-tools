"""
AI教育助手工具集

提供了一系列用于教育场景的AI工具，包括：
- 知识点提取
- 练习题生成
- 资源搜索
"""

from .knowledge_extractor import (
    KnowledgePoint,
    KnowledgeExtractor,
    extract_knowledge_points
)
from .exercise_generator import (
    Exercise,
    ExerciseSet,
    ExerciseGenerator
)
from .knowledge_search import (
    Resource,
    ResourceList,
    KnowledgeSearcher,
    search_resources
)

__all__ = [
    # 知识点提取
    'KnowledgePoint',
    'KnowledgeExtractor',
    'extract_knowledge_points',
    
    # 练习题生成
    'Exercise',
    'ExerciseSet',
    'ExerciseGenerator',
    
    # 资源搜索
    'Resource',
    'ResourceList',
    'KnowledgeSearcher',
    'search_resources'
]

# 版本信息
__version__ = '0.1.0'
__author__ = 'AI Education Team'
__description__ = 'AI tools for education'