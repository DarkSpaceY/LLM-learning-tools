from typing import List, Dict, Any
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class Resource(BaseModel):
    """学习资源"""
    title: str = Field(description="资源标题")
    url: str = Field(description="资源链接")
    type: str = Field(description="资源类型(video/doc/exercise)")
    description: str = Field(description="资源描述")


class Section(BaseModel):
    """章节内容"""
    title: str = Field(description="章节标题")
    content: List[str] = Field(description="章节内容要点")
    resources: List[Resource] = Field(description="相关学习资源")
    estimated_hours: int = Field(description="预计学习时间(小时)")


class Chapter(BaseModel):
    """学习章节"""
    title: str = Field(description="章节标题")
    sections: List[Section] = Field(description="小节列表")
    difficulty: str = Field(description="难度级别(beginner/intermediate/advanced)")
    prerequisites: List[str] = Field(description="前置知识要求")


class LearningPlan(BaseModel):
    """学习计划"""
    topic: str = Field(description="学习主题")
    description: str = Field(description="主题描述")
    chapters: List[Chapter] = Field(description="章节列表")
    total_hours: int = Field(description="总学习时长(小时)")
    target_audience: str = Field(description="目标受众")
    learning_goals: List[str] = Field(description="学习目标")


class LearningPlanner:
    def __init__(self, llm: LLM):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=LearningPlan)
        
        self.prompt = PromptTemplate(
            template=(
                "请为以下主题制定详细的学习计划。\n\n"
                "主题：{topic}\n"
                "难度要求：{difficulty}\n"
                "时间预期：{expected_hours}小时\n\n"
                "要求：\n"
                "1. 合理规划学习章节\n"
                "2. 设定明确的学习目标\n"
                "3. 推荐优质学习资源\n"
                "4. 注意知识点衔接\n"
                "5. 适合目标受众\n\n"
                "请按以下格式输出：\n{format_instructions}\n"
            ),
            input_variables=["topic", "difficulty", "expected_hours"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            }
        )

    async def plan(self, topic: str, difficulty: str = "beginner", expected_hours: int = 40) -> Dict[str, Any]:
        """生成学习计划"""
        try:
            # 生成并格式化提示
            prompt = self.prompt.format(
                topic=topic,
                difficulty=difficulty,
                expected_hours=expected_hours
            )
            
            # 使用LLM生成结果
            output = self.llm(prompt)
            
            # 解析输出
            learning_plan = self.parser.parse(output)
            
            # 返回结果
            return {
                "plan": learning_plan.dict(),
                "metadata": {
                    "topic": topic,
                    "difficulty": difficulty,
                    "expected_hours": expected_hours,
                    "success": True
                }
            }
        except Exception as e:
            print(f"学习计划生成失败: {str(e)}")
            return {
                "plan": {
                    "topic": topic,
                    "description": "计划生成失败",
                    "chapters": [],
                    "total_hours": expected_hours,
                    "target_audience": "未知",
                    "learning_goals": []
                },
                "metadata": {
                    "topic": topic,
                    "difficulty": difficulty,
                    "expected_hours": expected_hours,
                    "success": False,
                    "error": str(e)
                }
            }