from typing import Dict, Any
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class KnowledgePoint(BaseModel):
    """知识点结构"""
    title: str = Field(description="知识点标题")
    description: str = Field(description="知识点描述")
    importance: int = Field(description="重要程度(1-5)")
    related_concepts: list[str] = Field(description="相关概念")


class KnowledgeExtractor:
    def __init__(self, llm: LLM):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=KnowledgePoint)
        
        self.prompt = PromptTemplate(
            template=(
                "请分析以下文本，提取其中的重要知识点。\n\n"
                "要求：\n"
                "1. 找出最重要的知识点\n"
                "2. 给出清晰的描述\n"
                "3. 标记重要程度(1=基础，5=关键)\n"
                "4. 列出相关的概念\n\n"
                "文本内容：{text}\n\n"
                "请按以下格式输出：\n{format_instructions}\n"
            ),
            input_variables=["text"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            }
        )

    async def extract(self, text: str) -> Dict[str, Any]:
        """从文本中提取知识点"""
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
                "raw_text": text
            }
        except Exception as e:
            print(f"知识点提取失败: {str(e)}")
            return {
                "knowledge_point": {
                    "title": "提取失败",
                    "description": "无法从文本中提取知识点",
                    "importance": 1,
                    "related_concepts": []
                },
                "raw_text": text
            }

    def format_output(self, result: Dict[str, Any]) -> str:
        """格式化输出为易读的文本"""
        kp = result["knowledge_point"]
        stars = "⭐" * kp["importance"]
        concepts = ", ".join(kp["related_concepts"])
        
        return (
            f"📚 {kp['title']}\n\n"
            f"💡 描述：\n{kp['description']}\n\n"
            f"🌟 重要程度：{stars}\n\n"
            f"🔗 相关概念：\n{concepts}"
        )


async def extract_knowledge_points(
    text: str,
    llm: LLM,
    format_output: bool = True
) -> str:
    """提取知识点的工具函数"""
    extractor = KnowledgeExtractor(llm)
    result = await extractor.extract(text)
    
    if format_output:
        return extractor.format_output(result)
    return str(result)