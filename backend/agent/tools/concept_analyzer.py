from typing import List, Dict, Any
from pydantic import BaseModel
from langchain.llms.base import BaseLLM

class Concept(BaseModel):
    """概念数据模型"""
    id: str
    name: str
    description: str
    category: str  # 概念类别
    difficulty: int  # 1-5表示难度等级
    related_concepts: List[str]  # 相关概念
    examples: List[str]  # 示例
    applications: List[str]  # 应用场景
    key_points: List[str]  # 关键要点

class ConceptAnalyzer:
    """概念分析器"""
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    async def analyze_concept(self, concept_name: str, context: str = "") -> Concept:
        """分析概念"""
        prompt = f"""请分析以下概念：
        概念名称：{concept_name}
        相关上下文：{context}
        
        请按照以下格式返回JSON：
        {{
            "id": "唯一标识符",
            "name": "{concept_name}",
            "description": "概念描述",
            "category": "概念类别",
            "difficulty": "难度等级(1-5)",
            "related_concepts": ["相关概念列表"],
            "examples": ["示例列表"],
            "applications": ["应用场景列表"],
            "key_points": ["关键要点列表"]
        }}
        """
        
        try:
            response = await self.llm.agenerate([prompt])
            result = response.generations[0][0].text
            # 解析LLM返回的JSON结果
            import json
            data = json.loads(result)
            return Concept(**data)
        except Exception as e:
            raise ValueError(f"分析概念失败：{str(e)}")

    async def find_related_concepts(self, concept: Concept) -> List[Dict[str, Any]]:
        """查找相关概念"""
        prompt = f"""请查找与以下概念相关的其他概念：
        概念名称：{concept.name}
        概念描述：{concept.description}
        当前相关概念：{', '.join(concept.related_concepts)}
        
        请详细说明每个相关概念的关联度和重要性。
        """
        
        try:
            response = await self.llm.agenerate([prompt])
            result = response.generations[0][0].text
            
            # 解析相关概念
            related_concepts = []
            for concept_name in concept.related_concepts:
                related_concepts.append({
                    "name": concept_name,
                    "relevance": "high",  # 可以根据分析结果设置
                    "importance": "critical",  # 可以根据分析结果设置
                    "relationship_type": "prerequisite"  # 可以根据分析结果设置
                })
            
            return related_concepts
        except Exception as e:
            raise ValueError(f"查找相关概念失败：{str(e)}")

    async def explain_concept(self, concept: Concept, user_level: int) -> Dict[str, Any]:
        """根据用户水平解释概念"""
        prompt = f"""请根据用户水平解释以下概念：
        概念名称：{concept.name}
        概念描述：{concept.description}
        用户水平：{user_level}（1-5）
        
        请提供适合该用户水平的解释和示例。
        """
        
        try:
            response = await self.llm.agenerate([prompt])
            explanation = response.generations[0][0].text
            
            return {
                "concept_id": concept.id,
                "explanation": explanation,
                "examples": concept.examples,
                "key_points": concept.key_points,
                "difficulty_level": concept.difficulty,
                "suggested_prerequisites": [],  # 可以根据用户水平推荐前置概念
                "next_steps": []  # 可以推荐后续学习内容
            }
        except Exception as e:
            raise ValueError(f"解释概念失败：{str(e)}")

    async def compare_concepts(self, concepts: List[Concept]) -> Dict[str, Any]:
        """比较多个概念"""
        if len(concepts) < 2:
            raise ValueError("需要至少两个概念进行比较")
        
        prompt = f"""请比较以下概念：
        概念列表：{', '.join(c.name for c in concepts)}
        
        请分析这些概念之间的异同点和关系。
        """
        
        try:
            response = await self.llm.agenerate([prompt])
            analysis = response.generations[0][0].text
            
            return {
                "concepts": [c.name for c in concepts],
                "analysis": analysis,
                "similarities": [],  # 相似点列表
                "differences": [],  # 差异点列表
                "relationships": [],  # 概念间的关系
                "comparison_matrix": []  # 比较矩阵
            }
        except Exception as e:
            raise ValueError(f"比较概念失败：{str(e)}")

    async def generate_concept_map(self, concept: Concept, depth: int = 1) -> Dict[str, Any]:
        """生成概念图"""
        prompt = f"""请为以下概念生成概念图：
        中心概念：{concept.name}
        描述：{concept.description}
        深度：{depth}
        
        请分析概念之间的层次关系和连接。
        """
        
        try:
            response = await self.llm.agenerate([prompt])
            result = response.generations[0][0].text
            
            # 返回概念图数据结构
            return {
                "central_concept": {
                    "id": concept.id,
                    "name": concept.name,
                    "description": concept.description
                },
                "nodes": [  # 概念节点
                    {
                        "id": f"node_{i}",
                        "name": related,
                        "level": 1
                    } for i, related in enumerate(concept.related_concepts)
                ],
                "edges": [  # 概念关系
                    {
                        "source": concept.id,
                        "target": f"node_{i}",
                        "relationship": "related"
                    } for i in range(len(concept.related_concepts))
                ],
                "levels": depth,  # 概念图深度
                "metadata": {  # 额外信息
                    "total_nodes": len(concept.related_concepts) + 1,
                    "total_edges": len(concept.related_concepts)
                }
            }
        except Exception as e:
            raise ValueError(f"生成概念图失败：{str(e)}")