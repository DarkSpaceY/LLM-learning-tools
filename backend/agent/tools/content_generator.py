from typing import List, AsyncGenerator, Dict, Any
from dataclasses import dataclass, field
from langchain.llms.base import LLM


# 提示词模板
PROMPT_TEMPLATES = {
    "main_outline": """
你是一个专业的教育内容编辑。请为主题【{topic}】生成一个主要章节大纲。

要求：
1. 按照难度递进的顺序组织内容
2. 生成5-10个主要章节（一级标题）
3. 用"# "开头表示一级标题（注意#后面要有空格）
4. 每个章节标题简洁明确
5. 每个章节必须包含标题和描述
6. 章节描述必须用<>括起来
7. 格式要求非常严格，必须完全按照以下格式：
# 第n章 标题
<章节描述内容>

8. 章节描述要求：
   - 说明关键知识点和技能目标
   - 点明与其他章节的关联

示例：
# 第1章 基础定义
<本章介绍基本概念和核心定义，帮助读者建立基础认知>
# 第2章 简单公式
<本章探讨基本公式的应用和推导过程>

请直接开始输出大纲：
""",
    
    "chapter_outline": """
你是一个专业的教学大纲编辑。请为主题【{topic}】的章节【{chapter}】生成小节大纲。

章节描述：{description}

规则：
1. 小节结构（5-10个小节）：
   - 从概念到实践：先介绍必要理论，然后立即通过实践加深理解
   - 循序渐进：按照难度递进的顺序组织小节内容（在章节主题覆盖范围内）
   - 每个小节可包含多个知识点和技能
   - 小节标题简洁明了，能准确反映内容
2. 每个小节必须包含标题和描述
3. 小节描述要求：
   - 明确指出该小节的具体知识点
4. 格式要求非常严格，必须完全按照以下格式：

## 章节号.小节号 标题
<小节描述内容>

必须遵守：
1. 小节必须以"## "开头（注意##后面要有空格）
2. 章节号必须正确（如第1章就是1.1、1.2等，第2章就是2.1、2.2等）
3. 每个小节的描述必须用<>括起来
4. 每个小节之间必须有空行
5. 不要添加任何其他格式或内容

示例：
## {chapter_num}.1 变量定义
<介绍变量的基本概念和使用方法>
## {chapter_num}.2 数据类型
<详细讲解各种数据类型的特点和应用>

请直接按格式输出小节（不要加任何说明）：
""",
    
    "section_content": """
请为【{topic}】的小节【{section}】生成详细内容。

小节描述：{description}

内容组织：
   - 开篇点明本节学习的大部分知识点名称
   - 理论知识精简明了，避免冗长的背景介绍
   - 结尾总结本节知识点

要求：
1. 重要概念用加粗标记
2. 适当使用数学公式：
   - 行内公式用单个$包裹，如：$E=mc^2$
   - 块级公式用两个$$包裹
3. 适当使用图表辅助说明
4. 根据小节描述详细展开该小节的核心内容
5. 语言简洁易懂，逻辑清晰
6. 内容完整，包含示例和解释
7. 每段200-300字左右
8. 使用markdown格式，支持LaTeX公式
9. 分段输出，确保每段都有明确的主题
10.涉及数学概念时，优先使用数学公式表达

请直接开始生成内容：
"""
}


@dataclass
class Chapter:
    """章节数据结构"""
    number: int
    title: str
    description: str
    sections: List['Section'] = field(default_factory=list)


@dataclass
class Section:
    """小节数据结构"""
    number: str  # 如 "1.1"
    title: str
    description: str
    content: str = ""


async def generate_main_outline(
    topic: str,
    llm: LLM
) -> AsyncGenerator[Dict[str, Any], None]:
    """生成主要章节大纲"""
    prompt = PROMPT_TEMPLATES["main_outline"].format(topic=topic)
    print("\n生成章节大纲...")
    print("话题:", topic)
    print("提示词:", prompt)
    
    content = ""
    chapters = []
    
    async for chunk in llm._call(prompt):
        if not chunk:
            continue

        # 立即发送chunk实现流式效果
        if chunk != "":
            yield {
                "type": "chunk",
                "data": chunk
            }
            content += chunk
    
    # 处理完整内容生成章节列表
    current_title = ""
    current_desc = ""
    chapter_number = 0
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 处理章节标题
        if line.startswith('# '):
            # 如果有上一个章节，保存它
            if current_title:
                chapters.append(Chapter(
                    number=chapter_number,
                    title=current_title,
                    description=current_desc.strip()
                ))
            
            line = line[2:].strip()  # 移除 # 和空白
            # 尝试匹配"第n章 标题"格式
            if line.startswith('第') and '章' in line:
                try:
                    # 提取章节号和标题
                    chapter_part = line[1:line.index('章')].strip()
                    title_base = line[line.index('章')+1:].strip()
                    title_part = title_base.split('\n')[0].strip()
                    
                    # 转换章节号为数字
                    chapter_number = int(chapter_part)
                    # 开始新章节
                    current_title = f"第{chapter_part}章 {title_part}"
                    current_desc = ""
                except (ValueError, IndexError) as e:
                    print(f"\n章节格式解析失败: {line}")
                    print(f"错误信息: {str(e)}")
                    continue
        # 处理章节描述
        elif current_title and not line.startswith('#'):
            if line.startswith('<') and line.endswith('>'):
                current_desc = line[1:-1].strip()  # 移除 <> 并清理空白
    
    # 保存最后一个章节
    if current_title:
        chapters.append(Chapter(
            number=chapter_number,
            title=current_title,
            description=current_desc
        ))
    
    if not chapters:
        print("\n未能识别任何章节!")
        print("完整响应内容:")
        print("-" * 40)
        print(content)
        print("-" * 40)
        raise ValueError("未能正确解析章节内容")
        
    # 返回完整的章节列表
    yield {
        "type": "chapters",
        "data": chapters
    }


async def generate_chapter_outline(
    topic: str,
    chapter: Chapter,
    llm: LLM
) -> AsyncGenerator[Dict[str, Any], None]:
    """生成章节的小节大纲"""
    prompt = PROMPT_TEMPLATES["chapter_outline"].format(
        topic=topic,
        chapter=chapter.title,
        description=chapter.description,
        chapter_num=chapter.number
    )
    
    print(f"\n生成第 {chapter.number} 章小节...")
    print("提示词:", prompt)
    
    content = ""
    sections = []
    
    async for chunk in llm._call(prompt):
        if not chunk:
            continue
            
        # 立即发送chunk实现流式效果
        if chunk != "":
            yield {
                "type": "chunk",
                "data": chunk
            }
            content += chunk
    
    # 处理完整内容生成小节列表
    current_title = ""
    current_desc = ""
    current_number = ""
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 处理小节标题
        if line.startswith('## '):
            # 如果有上一个小节，保存它
            if current_title and current_number:
                sections.append(Section(
                    number=current_number,
                    title=current_title,
                    description=current_desc.strip()
                ))
            
            line = line[3:].strip()  # 移除 ## 和空白
            try:
                # 分割章节号和标题
                section_parts = line.split(' ', 1)
                if len(section_parts) != 2:
                    continue
                    
                section_number, section_title = section_parts
                
                # 验证章节号格式
                if '.' not in section_number:
                    continue
                    
                # 验证章节号与当前章节匹配
                main_chapter = section_number.split('.')[0]
                if int(main_chapter) != chapter.number:
                    continue
                
                # 开始新小节
                current_number = section_number
                current_title = section_title
                current_desc = ""
                
            except (ValueError, IndexError) as e:
                print(f"\n小节格式解析失败: {line}")
                print(f"错误信息: {str(e)}")
                continue
                
        # 处理小节描述
        elif current_title and not line.startswith('#'):
            if line.startswith('<') and line.endswith('>'):
                current_desc = line[1:-1].strip()  # 移除 <> 并清理空白
    
    # 保存最后一个小节
    if current_title and current_number:
        sections.append(Section(
            number=current_number,
            title=current_title,
            description=current_desc
        ))
    
    if not sections:
        print("\n未能提取到任何小节")
        print("完整响应内容:")
        print("-" * 40)
        print(content)
        print("-" * 40)
        print("\n错误原因：小节格式必须是：## 章节号.小节号 标题")
        print("正确示例：## 1.1 变量定义")
        raise ValueError("未识别到任何符合格式的小节")
    
    # 返回完整的小节列表
    yield {
        "type": "sections",
        "data": sections
    }


async def generate_section_content(
    topic: str,
    section: Section,
    llm: LLM
) -> AsyncGenerator[Dict[str, Any], None]:
    """生成小节的详细内容"""
    # 直接使用小节的标题和描述构建提示词
    prompt = PROMPT_TEMPLATES["section_content"].format(
        topic=topic,
        section=f"{section.number} {section.title}",
        description=section.description
    )
    content = ""
    async for chunk in llm._call(prompt):
        if not chunk:
            continue
        # 发送流式chunk
        yield {
            "type": "chunk",
            "data": chunk
        }
        content += chunk
    
    # 返回完整内容
    yield {
        "type": "content",
        "data": content
    }

# 导出内容
__all__ = [
    "Chapter",
    "Section",
    "generate_main_outline",
    "generate_chapter_outline",
    "generate_section_content"
]
