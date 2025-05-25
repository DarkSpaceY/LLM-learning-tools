from typing import Dict, Any, List
from pydantic import BaseModel
from langchain.llms.base import BaseLLM

class SimulationComponent(BaseModel):
    """仿真组件数据模型"""
    id: str
    name: str
    code: str  # 组件的前端代码
    properties: Dict[str, Any]  # 组件属性

class SimulationEnvironment(BaseModel):
    """仿真环境数据模型"""
    id_: str
    title: str
    description: str
    code: str  # 整体仿真环境的前端代码
    parameters: Dict[str, Any]  # 环境参数

class SimulationBuilder:
    """仿真构建器"""
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    async def create_simulation(self, topic: str) -> SimulationEnvironment:
        """创建仿真环境"""
        prompt = f"""请为以下主题创建一个基于HTML5 Canvas的仿真环境：
        主题：{topic}"""+"""
        
        代码结构要求：
        1. HTML结构必须包含：
           - 完整的DOCTYPE和meta标签
           - Canvas元素（设置合适的宽高）
           - 必要的容器和控制元素
           必须包含以下标签和元素：
           - <!DOCTYPE html>
           - <html>
           - <head>
           - <meta charset>
           - <title>
           - <body>
        
        2. CSS要求：
           - 使用模块化的样式组织
           - 响应式布局适配
           - 统一的颜色和字体风格
        
        3. JavaScript代码规范：
           - 使用ES6+语法，必须包含：
             * const 和 let 声明
             * 函数定义
             * 事件监听器
             * requestAnimationFrame
           - 采用模块化设计模式
           - 实现完整的生命周期管理
           - 清晰的事件处理机制
        
        4. Canvas绘制规范：
           - 使用requestAnimationFrame实现动画
           - 实现基本的碰撞检测
           - 合理使用Canvas状态栈
           - 优化绘制性能
           必须包含以下Canvas设置：
           - getContext('2d')
           - canvas.width
           - canvas.height
        
        5. 交互功能要求：
           - 必须实现以下至少一种事件响应：
             * click
             * mousemove
             * mousedown
             * mouseup
           - 添加基本的UI控制元素
           - 支持参数调节和状态重置
        
        6. 代码注释和文档：
           - 添加完整的函数文档注释
           - 关键算法和逻辑说明
           - 使用示例和参数说明
        
        7. 代码安全要求：
           - 禁止使用以下危险特性：
             * document.write()
             * eval()
             * innerHTML 直接赋值
        
        示例代码结构：
        ```html
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>仿真环境</title>
            <style>
                /* 样式定义 */
            </style>
        </head>
        <body>
            <canvas id="simulationCanvas"></canvas>
            <div class="controls">
                <!-- 控制元素 -->
            </div>
            <script>
                // 初始化代码
                const canvas = document.getElementById('simulationCanvas');
                const ctx = canvas.getContext('2d');
                
                // 状态管理
                let state = {
                    // 仿真状态变量
                };
                
                // 动画循环
                function animate() {
                    requestAnimationFrame(animate);
                    // 更新和绘制逻辑
                }
                
                // 事件处理
                canvas.addEventListener('click', (e) => {
                    // 交互逻辑
                });
                
                // 启动仿真
                animate();
            </script>
        </body>
        </html>
        ```
        
        请基于以上要求和示例，生成完整的仿真环境代码：
        """
        
        try:
            # 生成主要的仿真代码
            print(prompt)
            output = []
            async for chunk in self.llm._call(prompt):
                output.append(chunk)
                print(chunk,end="")
            simulation_code = ''.join(output)
            # 提取HTML代码块
            simulation_code = self._extract_code_block(simulation_code, 'html')
            # 验证代码的基本结构
            print(simulation_code)
            print(self._validate_code(simulation_code))
            if not self._validate_code(simulation_code):
                raise ValueError("生成的代码结构不完整或存在错误")
                
            # 创建仿真环境
            try:
                simulation = SimulationEnvironment(
                    id_=f"sim_{topic.lower().replace(' ', '_')}",
                    title=f"Simulation: {topic}",  # 添加主题到标题
                    description=f"A simulation environment for {topic}",
                    code=simulation_code,
                    parameters={}
                )
                print(simulation)
                return simulation
            except Exception as e:
                raise ValueError(f"创建SimulationEnvironment实例失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"创建仿真环境失败：{str(e)}")
    
    def _extract_code_block(self, text: str, language: str = None) -> str:
        """从文本中提取代码块
        
        Args:
            text: 包含代码块的文本字符串
            language: 代码块的语言标识（可选）
            
        Returns:
            str: 提取到的代码内容，如果没有找到则返回原文本
        """
        import re
        
        # 构建正则表达式模式
        if language:
            pattern = f"```{language}\\n([\\s\\S]*?)\\n```"
        else:
            pattern = "```([\\s\\S]*?)```"
            
        # 查找匹配的代码块
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return text

    def _validate_code(self, code: str) -> bool:
        """验证生成的代码的完整性和必要元素
        
        Args:
            code: 要验证的代码字符串
            
        Returns:
            bool: 验证是否通过
        """
        # HTML基本结构验证
        html_elements = [
            "<!DOCTYPE html>",
            "<html",
            "<head",
            "<meta charset",
            "<title",
            "<body"
        ]
        
        # Canvas相关验证
        canvas_elements = [
            "<canvas",
            "getContext('2d')",
            "canvas.width",
            "canvas.height"
        ]
        
        # JavaScript基本功能验证
        js_elements = [
            "function",
            "addEventListener",
            "requestAnimationFrame",
            "const",
            "let"
        ]
        
        # 事件处理验证
        event_elements = [
            "click",
            "mousemove",
            "mousedown",
            "mouseup"
        ]
        
        # 验证是否包含至少一个事件处理器
        has_event_handler = any(event in code for event in event_elements)
        
        # 验证基本结构和功能
        has_html_structure = all(element in code for element in html_elements)
        has_canvas_setup = all(element in code for element in canvas_elements)
        has_js_features = all(element in code for element in js_elements)
        
        # 验证是否包含错误的代码特征
        error_patterns = [
            "document.write(",  # 避免使用document.write
            "eval(",          # 避免使用eval
            "innerHTML ="      # 避免直接赋值innerHTML
        ]
        has_no_errors = not any(pattern in code for pattern in error_patterns)
        
        return all([
            has_html_structure,
            has_canvas_setup,
            has_js_features,
            has_event_handler,
            has_no_errors
        ])