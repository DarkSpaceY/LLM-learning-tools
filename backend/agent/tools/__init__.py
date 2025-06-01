"""
AI教育助手工具集

提供了一系列用于教育场景的AI工具，包括：
- 知识点提取
- 练习题生成
- 资源搜索
"""
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
from .knowledge_graph_generator import (
    KnowledgeNode,
    KnowledgeEdge,
    KnowledgeGraphGenerator
)
from .simulation_builder import (
    SimulationBuilder
)
from .content_generator import (
    generate_section_content
)

__all__ = [
    # 练习题生成
    'Exercise',
    'ExerciseSet',
    'ExerciseGenerator',
    
    # 资源搜索
    'Resource',
    'ResourceList',
    'KnowledgeSearcher',
    'search_resources',
    
    # 知识图谱
    'KnowledgeNode',
    'KnowledgeEdge',
    'KnowledgeGraphGenerator',
    
    # 仿真实验
    'SimulationBuilder',
    
    # 内容生成
    'generate_section_content'
]

# 版本信息
__version__ = '0.1.0'
__author__ = 'AI Education Team'
__description__ = 'AI tools for education'