from typing import List, Dict, Any
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class Exercise(BaseModel):
    """练习题结构"""
    question: str = Field(description="题目内容")
    options: List[str] = Field(description="选项列表(选择题)")
    answer: str = Field(description="正确答案")
    explanation: str = Field(description="答案解释")
    difficulty: str = Field(description="难度级别(easy/medium/hard)")
    topic: str = Field(description="题目主题")
    type: str = Field(description="题目类型(选择题/填空题/简答题)")
    keywords: List[str] = Field(description="相关关键词")


class ExerciseSet(BaseModel):
    """练习题集合"""
    exercises: List[Exercise] = Field(description="练习题列表")
    topic: str = Field(description="主题")
    difficulty: str = Field(description="整体难度")
    total_count: int = Field(description="题目总数")


class ExerciseGenerator:
    def __init__(self, llm: LLM):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=Exercise)
        
        self.prompt = PromptTemplate(
            template=(
                "请根据以下要求生成一道练习题。\n\n"
                "主题：{topic}\n"
                "难度：{difficulty}\n"
                "类型：{exercise_type}\n\n"
                "要求：\n"
                "1. 题目要清晰明确\n"
                "2. 选项要合理且有区分度\n"
                "3. 答案要有详细解释\n"
                "4. 难度要符合要求\n\n"
                "请按以下格式输出：\n{format_instructions}\n"
            ),
            input_variables=["topic", "difficulty", "exercise_type"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            }
        )

    async def generate(
        self,
        topic: str,
        difficulty: str = "medium",
        exercise_type: str = "选择题"
    ) -> Dict[str, Any]:
        """生成练习题"""
        try:
            # 生成并格式化提示
            prompt = self.prompt.format(
                topic=topic,
                difficulty=difficulty,
                exercise_type=exercise_type
            )
            
            # 使用LLM生成结果
            output = self.llm(prompt)
            
            # 解析输出
            exercise = self.parser.parse(output)
            
            # 返回结果
            return {
                "exercise": exercise.dict(),
                "metadata": {
                    "topic": topic,
                    "difficulty": difficulty,
                    "type": exercise_type
                }
            }
        except Exception as e:
            print(f"练习题生成失败: {str(e)}")
            return {
                "exercise": {
                    "question": "生成失败",
                    "options": ["选项生成失败"],
                    "answer": "无法生成答案",
                    "explanation": "练习题生成过程中出现错误",
                    "difficulty": difficulty,
                    "topic": topic,
                    "type": exercise_type,
                    "keywords": []
                },
                "metadata": {
                    "topic": topic,
                    "difficulty": difficulty,
                    "type": exercise_type
                }
            }

    def format_output(self, result: Dict[str, Any]) -> str:
        """格式化输出为易读的文本"""
        ex = result["exercise"]
        difficulty_map = {
            'easy': '简单 🟢',
            'medium': '中等 🟡',
            'hard': '困难 🔴'
        }
        
        diff = difficulty_map.get(ex['difficulty'], ex['difficulty'])
        
        # 构建基本信息
        output = [
            f"📝 练习题 ({diff})",
            f"📚 主题：{ex['topic']}",
            f"\n❓ 问题：\n{ex['question']}\n"
        ]
        
        # 如果是选择题，添加选项
        if ex['type'] == '选择题':
            for i, option in enumerate(ex['options'], start=1):
                output.append(f"{chr(64+i)}. {option}")
            output.append("")
        
        # 添加答案和解释
        output.extend([
            f"\n✅ 答案：{ex['answer']}",
            f"\n💡 解释：\n{ex['explanation']}",
            f"\n🏷️ 关键词：{', '.join(ex['keywords'])}"
        ])
        
        return "\n".join(output)


async def generate_exercise(
    topic: str,
    llm: LLM,
    difficulty: str = "medium",
    exercise_type: str = "选择题",
    format_output: bool = True
) -> str:
    """生成练习题的工具函数"""
    generator = ExerciseGenerator(llm)
    result = await generator.generate(topic, difficulty, exercise_type)
    
    if format_output:
        return generator.format_output(result)
    return str(result)