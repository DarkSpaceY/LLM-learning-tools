from typing import List, Dict, Any
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class KnowledgePoint(BaseModel):
    """知识点结构"""
    content: str = Field(description="知识点内容")
    importance: str = Field(description="重要程度(high/medium/low)")
    related_concepts: List[str] = Field(description="相关概念")
    prerequisites: List[str] = Field(description="前置知识")
    difficulty: str = Field(description="难度级别(basic/intermediate/advanced)")


class KnowledgePointSet(BaseModel):
    """知识点集合"""
    points: List[KnowledgePoint] = Field(description="知识点列表")
    topic: str = Field(description="主题")
    total_count: int = Field(description="知识点总数")


class KnowledgePointParser:
    def __init__(self, llm: LLM):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=KnowledgePoint)
        
        self.prompt = PromptTemplate(
            template=(
                "请分析以下文本，提取关键知识点。\n\n"
                "文本内容：{text}\n\n"
                "要求：\n"
                "1. 提取核心知识点\n"
                "2. 标注重要程度\n"
                "3. 列出相关概念\n"
                "4. 指出前置知识\n"
                "5. 评估难度级别\n\n"
                "请按以下格式输出：\n{format_instructions}\n"
            ),
            input_variables=["text"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            }
        )

    async def parse(self, text: str) -> Dict[str, Any]:
        """解析文本中的知识点"""
        try:
            # 生成并格式化提示
            prompt = self.prompt.format(text=text)
            
            # 使用LLM生成结果
            output = self.llm(prompt)
            
            # 解析输出
            knowledge_point = self.parser.parse(output)
            
            # 返回结果
            return {
                "knowledge_point": knowledge_point.dict(),
                "metadata": {
                    "text_length": len(text),
                    "success": True
                }
            }
        except Exception as e:
            print(f"知识点解析失败: {str(e)}")
            return {
                "knowledge_point": {
                    "content": "解析失败",
                    "importance": "low",
                    "related_concepts": [],
                    "prerequisites": [],
                    "difficulty": "basic"
                },
                "metadata": {
                    "text_length": len(text),
                    "success": False,
                    "error": str(e)
                }
            }