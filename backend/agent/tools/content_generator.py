from typing import List, AsyncGenerator, Dict, Any
from dataclasses import dataclass, field
from langchain.llms.base import LLM


# 提示词模板
PROMPT_TEMPLATES = {
    "main_outline": """
你是一个专业的教育内容编辑。请为主题【{topic}】生成一个主要章节大纲。

具体要求：
1. 章节数量和结构：
   - 根据主题复杂度和学习者水平合理安排章节数量（通常5-12个主要章节）
   - 每章节应该有明确的主题和学习目标
   - 章节之间要有清晰的层次关系
   - 章节应该是较大的概念范围或知识模块，内部再细分小节

2. 格式规范：
   - 用"# "开头表示一级标题（注意#后面要有空格）
   - 禁止使用`或```包裹内容
   - 每个章节标题简洁明确，突出关键概念
   - 章节描述必须用<>括起来
   - 严格按照以下格式：
     # 第n章 标题
     <章节描述内容>

3. 章节描述要求：
   - 明确指出本章的核心概念和关键知识点
   - 说明本章的具体学习目标和技能要求
   - 解释本章内容在整体知识体系中的地位
   - 点明与前后章节的关联和衔接
   - 提示本章的难点和重点
   - 确保描述的深度和难度符合学习者水平

示例：
# 第1章 基础定义
<本章介绍基本概念和核心定义。
根据学习者水平选择合适的解释方式和类比，帮助读者建立基础认知。>
# 第2章 简单公式
<本章探讨基本公式的应用和推导过程。
采用适合学习者认知水平的方式，帮助理解公式的含义和用法。>

章节组织原则：
1. 章节规划：
   - 章节为一个较大的范围，代表一个完整的知识模块
   - 内部会划分为更细的小节，不要在章节就具体化
   - 根据学习者水平调整知识点的深度和广度

2. 知识体系完整性：
   - 确保涵盖主题的所有核心概念和技能
   - 避免知识点遗漏和重复
   - 保持章节之间的逻辑关联，承上启下

3. 学习曲线设计：
   - 根据学习者认知特点设计学习路径
   - 按照认知规律和难度递进组织内容
   - 由浅入深，由简单到复杂
   - 新知识必须建立在已学内容的基础上
   - 确保每个概念的讲解深度符合学习者水平

4. 实践与应用：
   - 理论知识必须配合适合学习者水平的实践案例
   - 每个主要概念都应有相应的应用场景
   - 确保学习者能学以致用
   - 练习难度要符合学习者能力范围

联网搜索结果：
{web_context}

请直接开始输出大纲：
""",
    "chapter_outline_with_context": """
你是一个专业的教学大纲编辑。请为主题【{topic}】的章节【{chapter}】生成小节大纲。

章节描述：{description}

规则：
1. 小节结构（4-6个小节）：
   - 从概念到实践：先介绍必要理论，然后通过实践加深理解
   - 循序渐进：按照难度递进的顺序组织小节内容（在章节主题覆盖范围内，不得包含当前已生成的目录中其他章节的内容）
   - 每个小节代表一个较大的知识模块，可包含多个知识点
   - 小节标题要概括性强，能反映该模块的核心内容
   - 确保与已生成的章节保持一致性和连贯性
   - 如果主题指定了学习者层次（如小学、初中等），内容深度要符合该层次

2. 每个小节必须包含标题和描述
3. 小节描述要求：
   - 概括该小节包含的主要知识模块
   - 说明学习目标和掌握要求
   - 点明与其他小节的关联
   - 如有学习者层次要求，描述要符合认知水平

4. 格式要求非常严格，必须完全按照以下格式：
## 章节号.小节号 标题
<小节描述内容>

必须遵守：
1. 小节必须以"## "开头（注意##后面要有空格）
2. 章节号必须正确（如第1章就是1.1、1.2等，第2章就是2.1、2.2等）
3. 每个小节的描述必须用<>括起来
4. 禁止使用`或```包裹内容
5. 每个小节之间必须有空行
6. 不要添加任何其他格式或内容

示例：
## {chapter_num}.1 基础概念与原理
<本小节介绍核心概念和基本原理，建立知识框架。
包含关键术语定义、基本理论和重要性说明。
为后续学习打下基础。>

## {chapter_num}.2 方法与技巧
<本小节讲解实用方法和重要技巧。
通过典型案例展示应用方式。
帮助掌握实践要领。>

PS：当前已生成的目录：
{context}

联网搜索结果：
{web_context}

请直接按格式输出小节（不要加任何说明）：
""",
    "section_content_with_context": """
请为【{topic}】的小节【{section}】生成详细内容。

请你务必仔细、全面地阅读并深入理解下列的各项规则，包括提示词模板中的格式要求、内容结构设计、语言风格要求等每一个细节。在充分掌握这些规则的基础上，确保生成的内容严格遵循规则，无论是格式还是内容逻辑都能准确无误。

如果主题中提到了学习者的学历或学习层次（如小学、初中、高中、大学、研究生等），请特别注意：
1. 内容深度要与学习者水平相匹配
2. 使用符合该层次学习者认知水平的解释方式和类比
3. 示例和练习难度要适中，循序渐进
4. 专业术语的使用要根据学习者背景调整
5. 确保内容既有挑战性又不会造成挫败感
小节描述：{description}

严格限制条例：
- 绝对绝对不要使用或```markdown```或```text```或```math```等文本修饰符包裹内容，否则会出错。
- 禁止使用`或```包裹文字或公式，否则会出错。
- 在非代码相关主题中，绝对绝对禁止使用任何代码块。

当前已生成的目录：
{context}

语言风格要求：
    * 通俗易懂：优先使用简单词汇和短句。务必用生活化的类比、比喻和具体的、学习者熟悉的实例来解释抽象概念和原理。想象你在给一个聪明的外行朋友讲解。
    * 避免术语轰炸：引入必要术语时，必须立即用简单语言解释清楚。避免连续使用超过两个未解释的专业术语。
    * 逻辑清晰：使用清晰的连接词（首先、其次、因此、例如、然而等）引导思路。
        
内容结构设计：
1. 禁止用章节名作为标题！
小节标题作为标题，小节标题需要携带编号（如{section_number}）
次小节标题作为次级标题，次级标题也需要携带编号（如{section_number}.1）
示例：
# {section}
## {section_number}.1
## {section_number}.2
## {section_number}.3
...(至少包含5个次小节)

2. 正文部分：
   - 按知识点划分内容，每个知识点独立讲解，作为次小节标题，一个小节建议包含5-10个次小节。
   - **每一个次小节务必包含超过800字**，以全面且详尽的方式，将这个知识点的各个层面都解释得清清楚楚。
   - 概念讲解：
     * 定义和解释：用通俗易懂的语言准确定义每个概念，必要时结合生活化的类比
     * 特点和性质：详细说明概念的关键特征，突出重点和难点
     * 适用场景：解释概念的应用范围，明确使用限制和边界条件
     * 发展历史：简述概念的演变过程，加深理解
   - 原理分析：
     * 基本原理：深入浅出地解释核心原理，从直观认识到深层机制
     * 推导过程：分步骤展示关键的推导，确保每一步都清晰可理解
     * 证明方法：必要时提供严谨的证明，并辅以直观解释
     * 内在联系：阐明与其他概念的关联，构建知识网络
   - 应用示例：
     * 基础示例：从最简单的例子开始，逐步建立概念认知
     * 典型案例：结合实际场景，展示概念的标准应用方法
     * 进阶案例：提供复杂的实际应用，体现概念的深度和广度
     * 注意事项：详细指出常见错误和解决方案，总结经验教训
   - 巩固提升：
     * 要点总结：简明扼要地归纳关键知识点
     * 思考问题：设置启发性问题，引导深入思考
     * 练习建议：提供针对性的练习方向和方法

3. 结尾部分：
   - 扩展阅读：推荐进一步学习的资源(给出网站，书名或论文名称)

格式要求：
1. 文本格式：
   - 重要概念用**加粗**标记
   - 代码块使用```内容```形式
   - 非代码块严格禁止使用`或```包裹
   - 使用markdown格式规范

2. 数学公式：
   - 公式禁止使用`或```包裹
   - 公式：使用$$包裹，如：$$E=mc^2$$
   - 公式严格禁止使用$包裹！
   - 公式说明：解释每个符号的含义

3. 图表使用（推荐使用）：
   - 流程图：展示过程和步骤
   - 表格：系统归纳和对比

5. 代码示例：
   - 代码段包裹：使用```包裹，并指定语言
   - 完整性：确保代码可直接运行
   - 注释：详细解释关键步骤
   - 规范：遵循编码规范

6. 引用规范：
   - 内部引用：引用其他章节内容
   - 外部引用：引用参考资料
   - 注释说明：必要的补充解释

联网搜索结果：
{web_context}

直接开始生成内容：
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
    llm: LLM,
    context: str = None,
    web_context: str = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """生成主要章节大纲，失败时无限重试"""
    while True:
        try:
            # 根据是否有上下文选择提示词模板
            template_key = "main_outline"
            prompt = PROMPT_TEMPLATES[template_key].format(
                topic=topic,
                context=context if context else "",
                web_context=web_context if web_context else "未开启联网功能"
            )
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
            break  # 成功生成，退出循环
        except Exception as e:
            print(f"生成章节大纲失败: {str(e)}，正在重试...")
            continue


async def generate_chapter_outline(
    topic: str,
    chapter: Chapter,
    llm: LLM,
    context: str = None,
    web_context: str = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """生成章节的小节大纲，失败时无限重试"""
    while True:
        try:
            # 根据是否有上下文选择提示词模板
            template_key = "chapter_outline_with_context"
            prompt = PROMPT_TEMPLATES[template_key].format(
                topic=topic,
                chapter=chapter.title,
                description=chapter.description,
                chapter_num=chapter.number,
                context=context if context else "暂无",
                web_context=web_context if web_context else "未开启联网功能"
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
                        if str(main_chapter) != str(chapter.number):
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
            break  # 成功生成，退出循环
        except Exception as e:
            print(f"生成小节大纲失败: {str(e)}，正在重试...")
            continue


async def generate_section_content(
    topic: str,
    section: Section,
    llm: LLM,
    context: str = None,
    web_context: str = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """生成小节的详细内容，失败时无限重试"""
    while True:
        try:
    # 直接使用小节的标题和描述构建提示词
            # 根据是否有上下文选择提示词模板
            template_key = "section_content_with_context"
            prompt = PROMPT_TEMPLATES[template_key].format(
                topic=topic,
                section=f"{section.title}",
                description=section.description,
                context=context if context else "暂无",
                section_number=section.number,
                web_context=web_context if web_context else "未开启联网功能"
            )
            print(f"\n生成第 {section.number} 小节内容...")
            print("提示词:", prompt)
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
            break  # 成功生成，退出循环
        except Exception as e:
            print(f"生成小节内容失败: {str(e)}，正在重试...")
            continue

# 导出内容
__all__ = [
    "Chapter",
    "Section",
    "generate_main_outline",
    "generate_chapter_outline",
    "generate_section_content"
]
