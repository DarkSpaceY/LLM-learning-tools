from typing import List, Dict, Any
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from datetime import datetime
import random

class Resource(BaseModel):
    """学习资源结构"""
    id: str = Field(description="资源唯一标识")
    title: str = Field(description="资源标题")
    url: str = Field(description="资源链接")
    type: str = Field(description="资源类型(video/article/document/course/book/tool)")
    description: str = Field(description="资源描述")
    difficulty: int = Field(description="难度级别(1-5)")
    language: str = Field(description="资源语言(zh-CN/en-US)")
    tags: List[str] = Field(description="资源标签")
    rating: float = Field(description="评分(1-5)")
    reviewCount: int = Field(description="评价数量")
    author: str = Field(description="作者名称")
    authorAvatar: str = Field(description="作者头像URL")
    date: str = Field(description="发布日期")
    views: int = Field(description="浏览量")

class ResourceList(BaseModel):
    """资源列表结构"""
    data: List[Resource] = Field(description="资源列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")


class KnowledgeSearcher:
    def __init__(self, llm: LLM):
        self.llm = llm
        
        self.prompt = PromptTemplate(
            template=(
                "请为以下主题推荐一个高质量的学习资源。\n\n"
                "主题：{topic}\n"
                "难度要求：{difficulty}\n"
                "资源类型：{resource_type}\n\n"
                "要求：\n"
                "1. 资源必须真实可靠，优先推荐权威平台的内容\n"
                "2. 优先推荐中文资源，对于技术类内容可以推荐优质英文资源\n"
                "3. 详细描述资源内容，包括核心知识点和学习收益\n"
                "4. 给出推荐理由，说明资源的特色和适用人群\n"
                "5. 确保资源的难度级别与要求相符\n\n"
                "请按以下格式输出：\n"
                "📚 标题：[资源标题]\n"
                "🔗 链接：[资源链接]\n"
                "📝 类型：[资源类型] | 难度：[难度级别] | 语言：[资源语言]\n"
                "💡 描述：\n[资源描述]\n"
                "⭐ 推荐指数：[1-5分]\n"
                "🏷️ 标签：[#标签1 #标签2 ...]\n"
            ),
            input_variables=["topic", "difficulty", "resource_type"]
        )

    def _parse_formatted_output(self, text: str) -> List[Dict[str, Any]]:
        """解析格式化的输出文本"""
        try:
            resources = []
            current_resource = {}
            lines = text.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                if not line:  # 跳过空行
                    i += 1
                    if current_resource:  # 如果当前有资源，保存它
                        resources.append(current_resource)
                        current_resource = {}
                    continue
                
                if '📚 标题：' in line:
                    if current_resource:  # 如果遇到新资源，保存当前资源
                        resources.append(current_resource)
                        current_resource = {}
                    current_resource['id'] = f"res_{len(resources) + 1}_{random.randint(1000, 9999)}"
                    current_resource['title'] = line.split('：', 1)[1].strip()
                elif '🔗 链接：' in line:
                    current_resource['url'] = line.split('：', 1)[1].strip()
                elif '📝 类型：' in line:
                    parts = line.split('|')
                    current_resource['type'] = parts[0].split('：', 1)[1].strip().lower()
                    current_resource['difficulty'] = int(parts[1].split('：', 1)[1].strip()[0])
                    current_resource['language'] = parts[2].split('：', 1)[1].strip()
                elif '💡 描述：' in line:
                    desc_lines = []
                    i += 1
                    while i < len(lines) and not any(marker in lines[i] for marker in ['👤', '⭐', '🏷️']):
                        desc_lines.append(lines[i].strip())
                        i += 1
                    current_resource['description'] = '\n'.join(desc_lines).strip()
                    continue
                elif '👤 作者：' in line:
                    current_resource['author'] = line.split('：', 1)[1].strip()
                    current_resource['authorAvatar'] = f"https://api.dicebear.com/7.x/avataaars/svg?seed={current_resource['author']}"
                elif '⭐ 评分：' in line:
                    parts = line.split('|')
                    current_resource['rating'] = float(parts[0].split('：', 1)[1].strip().split('-')[0])
                    current_resource['reviewCount'] = int(parts[1].split('：', 1)[1].strip().split()[0])
                    current_resource['views'] = int(parts[2].split('：', 1)[1].strip().split()[0])
                elif '🏷️ 标签：' in line:
                    tags_str = line.split('：', 1)[1].strip()
                    current_resource['tags'] = [tag.strip('#') for tag in tags_str.split() if tag.startswith('#')]
                    current_resource['date'] = datetime.now().strftime("%Y-%m-%d")
                
                i += 1
            
            if current_resource:  # 保存最后一个资源
                resources.append(current_resource)
            
            return resources
        except Exception as e:
            raise ValueError(f"解析输出失败: {str(e)}")

    def _parse_formatted_output(self, text: str) -> List[Dict[str, Any]]:
        """解析格式化的输出文本"""
        try:
            resources = []
            current_resource = {}
            lines = text.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                if not line:  # 跳过空行
                    i += 1
                    if current_resource:  # 如果当前有资源，保存它
                        resources.append(current_resource)
                        current_resource = {}
                    continue
                
                if '📚 标题：' in line:
                    if current_resource:  # 如果遇到新资源，保存当前资源
                        resources.append(current_resource)
                        current_resource = {}
                    current_resource['id'] = f"res_{len(resources) + 1}_{random.randint(1000, 9999)}"
                    current_resource['title'] = line.split('：', 1)[1].strip()
                elif '🔗 链接：' in line:
                    current_resource['url'] = line.split('：', 1)[1].strip()
                elif '📝 类型：' in line:
                    parts = line.split('|')
                    current_resource['type'] = parts[0].split('：', 1)[1].strip().lower()
                    current_resource['difficulty'] = int(parts[1].split('：', 1)[1].strip()[0])
                    current_resource['language'] = parts[2].split('：', 1)[1].strip()
                elif '💡 描述：' in line:
                    desc_lines = []
                    i += 1
                    while i < len(lines) and not any(marker in lines[i] for marker in ['👤', '⭐', '🏷️']):
                        desc_lines.append(lines[i].strip())
                        i += 1
                    current_resource['description'] = '\n'.join(desc_lines).strip()
                    continue
                elif '👤 作者：' in line:
                    current_resource['author'] = line.split('：', 1)[1].strip()
                    current_resource['authorAvatar'] = f"https://api.dicebear.com/7.x/avataaars/svg?seed={current_resource['author']}"
                elif '⭐ 评分：' in line:
                    parts = line.split('|')
                    current_resource['rating'] = float(parts[0].split('：', 1)[1].strip().split('-')[0])
                    current_resource['reviewCount'] = int(parts[1].split('：', 1)[1].strip().split()[0])
                    current_resource['views'] = int(parts[2].split('：', 1)[1].strip().split()[0])
                elif '🏷️ 标签：' in line:
                    tags_str = line.split('：', 1)[1].strip()
                    current_resource['tags'] = [tag.strip('#') for tag in tags_str.split() if tag.startswith('#')]
                    current_resource['date'] = datetime.now().strftime("%Y-%m-%d")
                
                i += 1
            
            if current_resource:  # 保存最后一个资源
                resources.append(current_resource)
            
            return resources
        except Exception as e:
            raise ValueError(f"解析输出失败: {str(e)}")

    async def search(
        self,
        query: str,
        resource_type: str = None,
        difficulty: int = 0,
        sort: str = "relevance",
        page: int = 1,
        page_size: int = 10,
        filters: Dict[str, Any] = None
    ) -> ResourceList:
        """搜索学习资源
        
        Args:
            query: 搜索关键词
            resource_type: 资源类型(video/article/document/course/book/tool)
            difficulty: 难度级别(0-5，0表示不限)
            sort: 排序方式(relevance/rating/date)
            page: 当前页码
            page_size: 每页数量
            filters: 过滤条件
            
        Returns:
            包含资源列表和元数据的字典
        """
        try:
            # 转换难度等级
            difficulty_map = {
                0: "不限",
                1: "入门",
                2: "基础",
                3: "进阶",
                4: "高级",
                5: "专家"
            }
            difficulty_text = difficulty_map.get(difficulty, "不限")
            
            # 生成并格式化提示
            prompt = self.prompt.format(
                topic=query,
                difficulty=difficulty_text,
                resource_type=resource_type or "不限"
            )
            
            # 使用LLM生成结果
            output = self.llm(prompt)
            
            # 解析格式化输出
            resources = self._parse_formatted_output(output)
            
            # 应用过滤和排序
            if resource_type:
                resources = [r for r in resources if r['type'] == resource_type.lower()]
            
            if difficulty > 0:
                resources = [r for r in resources if r['difficulty'] == difficulty]
            
            if sort == "rating":
                resources.sort(key=lambda x: (-x['rating'], -x['reviewCount']))
            elif sort == "date":
                resources.sort(key=lambda x: x['date'], reverse=True)
            
            # 分页
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paged_resources = resources[start_idx:end_idx]
            
            # 构建ResourceList对象
            return ResourceList(
                data=[Resource(**r) for r in paged_resources],
                total=len(resources),
                page=page,
                page_size=page_size
            )
            
        except Exception as e:
            print(f"资源搜索失败: {str(e)}")
            return ResourceList(
                data=[],
                total=0,
                page=page,
                page_size=page_size
            )

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