from typing import List, Dict, Any
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class Exercise(BaseModel):
    """练习题结构"""
    question: str = Field(description="题目内容")
    options: Dict[str, str] = Field(description="选项映射(选择题)，如{'A': '选项1', 'B': '选项2'}")
    answer: str = Field(description="正确答案")
    type_: str = Field(description="题目类型(multiple_choice/true_false/short_answer/fill_blank/calculation)")



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

    async def generate_batch(
        self,
        topic: str,
        types: List[str],
        difficulty: int = 3,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """批量生成练习题
        
        Args:
            topic: 知识点
            types: 题目类型列表
            difficulty: 难度等级(1-5)
            count: 生成数量
            
        Returns:
            List[Dict]: 生成的练习题列表
        """
        try:
            # 构建批量生成提示
            prompt = f"""请根据以下要求生成练习题：
            知识点：{topic}
            请你生成{count}道{', '.join(types)}（确保生成的题型正确，只能生成指定的题目类型！）
            难度等级：{difficulty}/5

            要求：
            1. 题目难度要符合指定等级
            2. 每道题必须包含题目类型、题干和答案
            3. 选择题的题干部分需要使用///分隔选项
            4. 填空题的题干部分需要填入地方的用____代替
            5. 判断题/计算题/简答题的题干是一个整体，无分隔

            各题型示例：
            选择题示例：
            <选择题|以下哪个是正确的字符串拼接方式///A. a = "hello" + "world"///B. a = ",".join(["hello", "world"]) ///C. a = str.concat("hello", "world")///D. a = "hello" % "world"|B>

            判断题示例：
            <判断题|Python中的列表是不可变数据类型|错误>

            填空题示例：
            <填空题|在Python中，使用____函数可以获取列表的长度|len>

            计算题示例：
            <计算题|一个列表[1,2,3,4,5]，请计算其所有元素的平均值|3>

            简答题示例：
            <简答题|简述Python中的列表推导式的优势|列表推导式提供了创建列表的简洁方式，具有以下优势：1. 代码更简洁优雅 2. 执行效率更高 3. 可读性好 4. 可以结合条件筛选>

            请使用以下格式输出每道题目：
            <题目类型|题干|答案>
            <题目类型|题干|答案>
            <题目类型|题干|答案>
            ...

            注意：
            - 选择题的题干部分需要使用/分隔选项
            - 填空题的题干部分需要填入地方的用____代替
            - 判断题/计算题/简答题的题干是一个整体，无分隔
            """
            
            # 初始化输出列表
            output = []
            
            # 使用LLM生成结果
            async for chunk in self.llm._call(prompt):
                output.append(chunk)
            output = ''.join(output)
            # 解析输出格式
            exercises = []
            for line in output.strip().split('\n'):
                line = line.strip()
                if line.startswith('<') and line.endswith('>'):
                    try:
                        # 移除尖括号并分割字段
                        fields = line[1:-1].split('|')
                        if len(fields) != 3:
                            continue
                            
                        exercise_type, question, answer = fields
                        
                        # 处理选项
                        options = {}
                        if exercise_type.strip() == '选择题':
                            option_list = question.strip().split('///')
                            if len(option_list) > 1:
                                question = option_list[0]
                                for i, opt in enumerate(option_list[1:], start=0):
                                    options[chr(65 + i)] = opt.strip()
                        
                        # 创建练习题对象
                        exercise_data = {
                            'question': question.strip(),
                            'options': options,
                            'answer': answer.strip(),
                            'type_': exercise_type.strip().lower().replace('题', ''),
                        }
                        
                        exercise = Exercise(**exercise_data)
                        exercises.append(exercise.dict())
                    except Exception as e:
                        print(f"题目解析失败: {str(e)}")
                        continue
            
            return exercises[:count]  # 确保返回指定数量的题目
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