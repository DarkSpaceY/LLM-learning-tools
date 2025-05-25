from typing import List, Dict, Any
from pydantic import BaseModel
from langchain.llms.base import BaseLLM
import re
import uuid
from typing import Optional

class Resource(BaseModel):
    """学习资源数据模型"""
    id: str
    title: str
    description: str
    type: str  # 资源类型：视频、文章、教程等
    url: str  # 资源链接
    difficulty: int  # 1-5表示难度等级

class ResourceSearcher:
    """学习资源搜索器"""
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.resource_database: List[Resource] = []  # 模拟资源数据库

    async def search_resources(self, query: str, resource_type: Optional[str] = None, difficulty: Optional[int] = None) -> List[Resource]:
        """搜索学习资源
        
        Args:
            query: 搜索关键词
            resource_type: 资源类型（可选）
            difficulty: 难度等级1-5（可选）
            
        Returns:
            List[Resource]: 资源列表
        """
        prompt = f"""请根据以下条件搜索学习资源：
        查询内容：{query}
        资源类型：{resource_type if resource_type else '所有类型'}
        难度等级：{difficulty if difficulty else '不限'}
        
        严格要求：
        1. 必须严格按照以下格式返回资源信息，不得添加任何额外内容
        2. 每个资源必须包含且仅包含5个字段：标题、描述、类型、URL和难度
        3. 难度必须是1-5的整数
        4. 所有字段使用|分隔，整个资源信息用<>包裹
        
        格式：<标题|描述|类型|URL|难度>
        示例：<Python入门教程|适合初学者的Python教程|视频|https://example.com/python|3>
        
        请返回3-5个最相关的资源，每个资源占一行。
        """
        
        try:
            # 获取LLM响应
            result = []
            async for chunk in self.llm._call(prompt):
                result.append(chunk)
            result = ''.join(result)
            
            # 使用更严格的正则表达式匹配
            pattern = r'<([^>]+)>'
            matches = re.finditer(pattern, result)
            
            resources = []
            for match in matches:
                resource_str = match.group(1).strip()
                
                try:
                    # 分割并验证字段
                    parts = [part.strip() for part in resource_str.split('|')]
                    
                    if len(parts) != 5:
                        continue
                        
                    title, description, res_type, url, difficulty_str = parts
                    
                    # 验证必填字段
                    if not all([title, description, res_type, url, difficulty_str]):
                        continue
                        
                    # 验证难度值
                    try:
                        difficulty_val = int(difficulty_str)
                        if not 1 <= difficulty_val <= 5:
                            continue
                    except ValueError:
                        continue
                    
                    # 创建资源对象
                    resource = Resource(
                        id=str(uuid.uuid4()),
                        title=title,
                        description=description,
                        type=res_type,
                        url=url.replace('`', ''),  # 清理URL中的反引号
                        difficulty=difficulty_val
                    )
                    resources.append(resource)
                    
                except (ValueError, IndexError) as e:
                    # 记录具体错误但继续处理
                    print(f"解析资源失败: {str(e)}，资源字符串: {resource_str}")
                    continue
            return resources
            
        except Exception as e:
            raise ValueError(f"搜索资源失败：{str(e)}")