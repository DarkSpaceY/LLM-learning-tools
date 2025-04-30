from typing import List, Dict, Any
from dataclasses import dataclass
from langchain.llms.base import LLM


@dataclass
class KnowledgeNode:
    """知识点节点"""
    id: str
    label: str  # 显示名称
    name: str  # 节点显示用名称（与label相同）
    description: str  # 简短描述
    category: str  # 类别（概念/方法/原理等）
    value: int = 1  # 节点大小权重
    draggable: bool = True  # 是否可拖拽
    tags: List[str] = None  # 标签
    metadata: Dict[str, Any] = None  # 元数据


@dataclass
class KnowledgeEdge:
    """知识点关系"""
    source: str  # 源节点ID
    target: str  # 目标节点ID
    type: str  # 关系类型（包含/依赖/相关等）
    description: str  # 关系描述
    label: str = ""  # 边的标签（与type相同）
    metadata: Dict[str, Any] = None  # 元数据


PROMPT_TEMPLATES = {
    "expand_knowledge": """
你是一个专业的知识图谱分析专家。请基于给定的知识点【{topic}】，生成相关的知识点。

要求：
1. 生成4-6个相关知识点
2. 每个知识点都要归类（概念/方法/原理/应用）
3. 为每个知识点提供简短描述（50字以内）
4. 指明与中心知识点的关系类型（包含/依赖/应用/相关/推导）

输出格式要求：
- 每个知识点用<node>标签包裹，属性用|分隔
- 属性顺序：id,label,category,description,relation
- id使用K1,K2,K3...格式

示例输出：
<node|K1,变量,概念,用于存储和表示数据的命名空间,包含>
<node|K2,数据类型,概念,定义数据的存储格式和操作方式,包含>

请直接开始输出：
"""
}


class KnowledgeGraphGenerator:
    def __init__(self, llm: LLM):
        self.llm = llm

    async def expand_knowledge(
        self,
        topic: str,
        description: str = "",
        category: str = "概念"  # 默认为概念类型
    ):
        """生成初始知识图谱"""
        prompt = PROMPT_TEMPLATES["expand_knowledge"].format(
            topic=topic
        )

        # 输出初始信息
        yield {
            "type": "chunk",
            "data": "开始生成知识图谱...\n"
        }

        # 创建根节点
        root_node = KnowledgeNode(
            id="center",
            label=topic,
            name=topic,
            category=category,
            description=description or f"知识点：{topic}",
            value=1,
            draggable=True
        )

        # 收集完整输出
        result = ""
        async for chunk in self.llm._call(prompt):
            if chunk:
                yield {
                    "type": "chunk",
                    "data": chunk
                }
                result += chunk

        yield {
            "type": "chunk",
            "data": "\n正在解析知识点和关系..."
        }
        
        # 解析输出
        lines = result.strip().split('\n')
        nodes = [root_node]  # 将根节点添加到节点列表
        edges = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('<node|'):
                # 解析节点
                attrs = line[6:-1].split(',')
                if len(attrs) >= 5:  # 确保包含关系属性
                    node = KnowledgeNode(
                        id=attrs[0],
                        label=attrs[1],
                        name=attrs[1],
                        category=attrs[2],
                        description=attrs[3],
                        value=1,
                        draggable=True
                    )
                    nodes.append(node)
                    
                    # 创建与中心节点的关系
                    if attrs[0] != "center":
                        edge = KnowledgeEdge(
                            source="center",
                            target=attrs[0],
                            type=attrs[4],  # 使用节点中的关系属性
                            description=f"{attrs[1]}是{topic}的{attrs[4]}",
                            label=attrs[4]
                        )
                        edges.append(edge)
        
        # 返回解析后的数据
        graph_data = {
            "nodes": [vars(node) for node in nodes],
            "edges": [vars(edge) for edge in edges]
        }

        yield {
            "type": "chunk",
            "data": f"\n已生成 {len(nodes)} 个知识点，{len(edges)} 个关系。"
        }

        yield {
            "type": "graph",
            "data": graph_data
        }

    async def expand_single_node(
        self,
        node_id: str,
        topic: str,
        description: str,
        category: str,
        current_nodes: List[Dict[str, Any]] = None
    ):
        """拓展单个知识点节点"""
        prompt = f"""
你是一个专业的知识图谱分析专家。请基于给定的知识点【{topic}】（{category}），生成相关的延伸知识点。

要拓展的中心知识点：
- ID: {node_id}
- 名称: {topic}
- 类别: {category}
- 描述: {description}

已有知识点：
{chr(10).join([
    f"- {node['label']}（{node['category']}）"
    for node in (current_nodes or [])
])}

要求：
1. 生成3-4个新的相关知识点（避免与已有知识点重复）
2. 每个知识点都要归类（概念/方法/原理/应用）
3. 为每个知识点提供简短描述（50字以内）
4. 指明与中心知识点的关系类型（包含/依赖/应用/相关/推导）

输出格式要求：
- 每个知识点用<node>标签包裹，属性用|分隔
- 属性顺序：id,label,category,description,relation
- id使用K1,K2,K3...格式

示例输出：
<node|K1,变量,概念,用于存储和表示数据的命名空间,包含>

请直接开始输出：
"""
        # 输出初始信息
        yield {
            "type": "chunk",
            "data": f"开始拓展知识点 [{topic}]...\n"
        }

        # 收集完整输出
        result = ""
        async for chunk in self.llm._call(prompt):
            if chunk:
                yield {
                    "type": "chunk",
                    "data": chunk
                }
                result += chunk

        yield {
            "type": "chunk",
            "data": "\n正在解析新的知识点和关系..."
        }
        
        # 解析输出
        lines = result.strip().split('\n')
        nodes = []
        edges = []
        node_counter = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('<node|'):
                # 解析节点
                attrs = line[6:-1].split(',')
                if len(attrs) >= 5:  # 确保包含关系属性
                    # 生成新的节点ID，使用原节点ID作为前缀
                    new_id = f"{node_id}-{node_counter}"
                    # 创建新节点
                    node = KnowledgeNode(
                        id=new_id,
                        label=attrs[1],
                        name=attrs[1],
                        category=attrs[2],
                        description=attrs[3],
                        value=1,
                        draggable=True
                    )
                    nodes.append(node)
                    
                    # 创建与父节点的关系边
                    edge = KnowledgeEdge(
                        source=node_id,  # 父节点作为源节点
                        target=new_id,   # 新节点作为目标节点
                        type=attrs[4],    # 使用节点中的关系属性
                        description=f"{attrs[1]}是{topic}的{attrs[4]}",
                        label=attrs[4]    # 使用关系类型作为标签
                    )
                    edges.append(edge)
                    node_counter += 1
        
        # 返回解析后的数据
        graph_data = {
            "nodes": [vars(node) for node in nodes],
            "edges": [vars(edge) for edge in edges]
        }

        yield {
            "type": "chunk",
            "data": f"\n已生成 {len(nodes)} 个新知识点，{len(edges)} 个关系。"
        }

        yield {
            "type": "graph",
            "data": graph_data
        }

    async def analyze_relation(
        self,
        source_node: KnowledgeNode,
        target_node: KnowledgeNode
    ) -> KnowledgeEdge:
        """分析两个知识点之间的关系"""
        prompt = PROMPT_TEMPLATES["analyze_relation"].format(
            source=source_node.label,
            source_desc=source_node.description,
            target=target_node.label,
            target_desc=target_node.description
        )
        
        result = ""
        async for chunk in self.llm._call(prompt):
            if chunk:
                result += chunk
        result = result.strip()
        
        # 解析关系
        if result.startswith('<relation|'):
            attrs = result[10:-1].split('|')
            if len(attrs) >= 3:
                return KnowledgeEdge(
                    source=source_node.id,
                    target=target_node.id,
                    type=attrs[0],
                    description=attrs[2]
                )
        
        return None