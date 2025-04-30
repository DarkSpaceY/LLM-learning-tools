from typing import List, Dict, Any
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class Resource(BaseModel):
    """学习资源结构"""
    title: str = Field(description="资源标题")
    url: str = Field(description="资源链接")
    type: str = Field(description="资源类型(文档/视频/课程等)")
    description: str = Field(description="资源描述")
    difficulty: str = Field(description="难度级别(beginner/intermediate/advanced)")
    language: str = Field(description="资源语言(zh-CN/en-US)")
    tags: List[str] = Field(description="资源标签")
    rating: float = Field(description="推荐指数(1-5)")


class ResourceList(BaseModel):
    """资源列表"""
    resources: List[Resource] = Field(description="资源列表")
    topic: str = Field(description="搜索主题")
    total_count: int = Field(description="资源总数")


class KnowledgeSearcher:
    def __init__(self, llm: LLM):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=Resource)
        
        self.prompt = PromptTemplate(
            template=(
                "请为以下主题推荐一个高质量的学习资源。\n\n"
                "主题：{topic}\n"
                "难度要求：{difficulty}\n"
                "资源类型：{resource_type}\n\n"
                "要求：\n"
                "1. 资源必须真实可靠\n"
                "2. 优先推荐中文资源\n"
                "3. 详细描述资源内容\n"
                "4. 给出推荐理由\n\n"
                "请按以下格式输出：\n{format_instructions}\n"
            ),
            input_variables=["topic", "difficulty", "resource_type"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            }
        )

    async def search(
        self,
        topic: str,
        difficulty: str = "beginner",
        resource_type: str = "文档"
    ) -> Dict[str, Any]:
        """搜索学习资源"""
        try:
            # 生成并格式化提示
            prompt = self.prompt.format(
                topic=topic,
                difficulty=difficulty,
                resource_type=resource_type
            )
            
            # 使用LLM生成结果
            output = self.llm(prompt)
            
            # 解析输出
            resource = self.parser.parse(output)
            
            # 返回结果
            return {
                "resource": resource.dict(),
                "metadata": {
                    "topic": topic,
                    "difficulty": difficulty,
                    "type": resource_type
                }
            }
        except Exception as e:
            print(f"资源搜索失败: {str(e)}")
            return {
                "resource": {
                    "title": "搜索失败",
                    "url": "",
                    "type": resource_type,
                    "description": "无法找到相关资源",
                    "difficulty": difficulty,
                    "language": "zh-CN",
                    "tags": [],
                    "rating": 0.0
                },
                "metadata": {
                    "topic": topic,
                    "difficulty": difficulty,
                    "type": resource_type
                }
            }

    def format_output(self, result: Dict[str, Any]) -> str:
        """格式化输出为易读的文本"""
        res = result["resource"]
        diff_map = {
            'beginner': '入门 🟢',
            'intermediate': '进阶 🟡',
            'advanced': '高级 🔴'
        }
        
        # 获取难度显示
        difficulty = diff_map.get(res['difficulty'], res['difficulty'])
        
        # 获取资源评分
        rating = "⭐" * int(res['rating'])
        
        # 生成标签字符串
        tags = " ".join([f"#{tag}" for tag in res['tags']])
        
        # 构建输出文本
        output = [
            f"📚 {res['title']}",
            f"类型：{res['type']} | 难度：{difficulty} | 语言：{res['language']}",
            f"\n🔗 {res['url']}",
            f"\n📝 描述：\n{res['description']}",
            f"\n⭐ 推荐指数：{rating}",
            f"\n🏷️ 标签：{tags}"
        ]
        
        return "\n".join(output)


async def search_resources(
    topic: str,
    llm: LLM,
    difficulty: str = "beginner",
    resource_type: str = "文档",
    format_output: bool = True
) -> str:
    """搜索学习资源的工具函数"""
    searcher = KnowledgeSearcher(llm)
    result = await searcher.search(topic, difficulty, resource_type)
    
    if format_output:
        return searcher.format_output(result)
    return str(result)