from typing import List, Dict, Any, AsyncGenerator
from pydantic import BaseModel
from langchain.llms.base import BaseLLM
import uuid

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

    async def analyze_concept(self, concept: str) -> Dict[str, Any]:
        """分析概念并返回完整的分析结果
        
        Args:
            concept: 概念名称
            
        Returns:
            Dict[str, Any]: 完整的分析结果，包含概念的定义、特征、示例、关系和应用场景
        """
        try:
            # 构建分析提示词
            prompt = f"""请分析以下概念：{concept}

请严格按照以下格式提供分析结果，确保每个部分的格式完全符合要求：

<定义>
用一段简洁明确的文字描述该概念的本质特征和核心含义
</定义>

<特征>
- 列出该概念的一个关键特征
- 列出该概念的另一个关键特征
（每个特征单独一行，以减号开头）
</特征>

<示例>
- 提供一个具体且容易理解的示例
- 提供另一个具体且容易理解的示例
（每个示例单独一行，以减号开头）
</示例>

<关系>
- 概念A~关系类型
- 概念B~关系类型
- 概念C~关系类型
（每个关系单独一行，以减号开头，冒号前为相关概念名称，冒号后为与主概念的关系类型）
</关系>

<应用>
- 描述一个具体的应用场景
- 描述另一个具体的应用场景
（每个应用场景单独一行，以减号开头）
</应用>

注意事项：
1. 所有内容必须严格按照上述格式书写，包括标签、减号、冒号等标记符号
2. 定义部分应该是一段完整的描述，不使用减号标记
3. 特征、示例和应用部分的每一项都必须单独一行，并以减号开头
4. 关系部分的每一项必须包含相关概念和关系类型，用冒号分隔
5. 所有内容应该实质性、具体且准确，避免空泛的描述

请确保输出格式的规范性和内容的专业性。
"""
            
            # 使用LLM生成分析结果，收集所有chunk
            result_chunks = []
            async for chunk in self.llm._call(prompt):
                result_chunks.append(chunk)
            result_text = ''.join(result_chunks)
            print(result_text)
            # 解析结果
            analysis_data = self._structure_raw_result(result_text)
            
            # 返回完整的分析结果
            return {
                "concept": concept,
                "definition": analysis_data.get('definition', ''),
                "characteristics": analysis_data.get('characteristics', []),
                "examples": analysis_data.get('examples', []),
                "relations": analysis_data.get('relations', []),
                "applications": analysis_data.get('applications', [])
            }
            
        except Exception as e:
            raise ValueError(f"概念分析失败：{str(e)}")
            
    def _structure_raw_result(self, raw_text: str) -> Dict[str, Any]:
        """将非JSON格式的原始文本结构化为字典格式
        
        Args:
            raw_text: LLM返回的原始文本
            
        Returns:
            Dict[str, Any]: 结构化后的数据
        """
        # 初始化结果字典
        result = {
            'definition': '',
            'characteristics': [],
            'examples': [],
            'relations': [],
            'applications': []
        }
        
        # 使用正则表达式匹配XML标签格式的内容
        import re
        
        # 定义部分
        definition_match = re.search(r'<定义>(.*?)</定义>', raw_text, re.DOTALL)
        if definition_match:
            result['definition'] = definition_match.group(1).strip()
        
        # 特征部分
        characteristics_match = re.search(r'<特征>(.*?)</特征>', raw_text, re.DOTALL)
        if characteristics_match:
            characteristics = characteristics_match.group(1).strip().split('\n')
            result['characteristics'] = [c.strip('- ').strip() for c in characteristics if c.strip('- ').strip()]
        
        # 示例部分
        examples_match = re.search(r'<示例>(.*?)</示例>', raw_text, re.DOTALL)
        if examples_match:
            examples = examples_match.group(1).strip().split('\n')
            result['examples'] = [e.strip('- ').strip() for e in examples if e.strip('- ').strip()]
        
        # 关系部分
        relations_match = re.search(r'<关系>(.*?)</关系>', raw_text, re.DOTALL)
        if relations_match:
            relations = relations_match.group(1).strip().split('\n')
            # 解析关系和类型
            parsed_relations = []
            for r in relations:
                r = r.strip('- ').strip()
                if not r:  # 跳过空行
                    continue
                if '~' in r:
                    concept, relationship = r.split('~', 1)
                    if concept and relationship:  # 确保概念和关系都不为空
                        parsed_relations.append({
                            'concept': concept.strip(),
                            'relationship': relationship.strip()
                        })
            result['relations'] = parsed_relations
        
        # 应用部分
        applications_match = re.search(r'<应用>(.*?)</应用>', raw_text, re.DOTALL)
        if applications_match:
            applications = applications_match.group(1).strip().split('\n')
            result['applications'] = [a.strip('- ').strip() for a in applications if a.strip('- ').strip()]
        
        return result