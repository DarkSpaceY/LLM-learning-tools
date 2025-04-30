import os
import sys
import json
import traceback
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

# 设置Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'learning-tree'))

# 导入本地模块
from agent import (  # noqa: E402
    langchain_agent,
    DEFAULT_MODEL,
    DEFAULT_BASE_URL,
    TIMEOUT
)
from tree import learning_tree_instance  # noqa: E402
from agent.tools.ollama_service import ollama_service  # noqa: E402
from settings_manager import settings_manager  # noqa: E402
from agent.tools.knowledge_graph_generator import (  # noqa: E402
    KnowledgeGraphGenerator
)
from agent.tools.knowledge_graph_manager import (  # noqa: E402
    KnowledgeGraphManager
)
from agent.tools.tutorial_manager import TutorialManager  # noqa: E402
from agent.tools.knowledge_point_parser import KnowledgePointParser  # noqa: E402
from agent.tools.exercise_generator import ExerciseGenerator  # noqa: E402
from agent.tools.resource_searcher import ResourceSearcher  # noqa: E402
from agent.tools.learning_plan_generator import LearningPlanGenerator  # noqa: E402
from agent.tools.concept_analyzer import ConceptAnalyzer  # noqa: E402
from agent.tools.simulation_builder import SimulationBuilder  # noqa: E402

# 初始化组件
knowledge_graph_generator = KnowledgeGraphGenerator(langchain_agent.llm)
knowledge_graph_manager = KnowledgeGraphManager()
tutorial_manager = TutorialManager()
knowledge_point_parser = KnowledgePointParser(langchain_agent.llm)
exercise_generator = ExerciseGenerator(langchain_agent.llm)
resource_searcher = ResourceSearcher(langchain_agent.llm)
learning_plan_generator = LearningPlanGenerator(langchain_agent.llm)
concept_analyzer = ConceptAnalyzer(langchain_agent.llm)
simulation_builder = SimulationBuilder(langchain_agent.llm)


# 初始化服务
app = FastAPI(
    title="AI Education Backend",
    description="Backend service for the AI Education application.",
    version="0.1.0"
)


# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 统一的响应模型
class ResponseModel(BaseModel):
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None


# 请求模型
class DialogueRequest(BaseModel):
    session_id: str
    message: str
    model: str = DEFAULT_MODEL


class ToolCallRequest(BaseModel):
    tool_name: str
    params: Dict[str, Any]
    model: str = DEFAULT_MODEL


class KnowledgeGraphRequest(BaseModel):
    topic: str
    model: str = DEFAULT_MODEL


class Settings(BaseModel):
    user_id: str
    preferences: Dict[str, Any]


class KnowledgePointRequest(BaseModel):
    content: str
    model: str = DEFAULT_MODEL


class ExerciseRequest(BaseModel):
    knowledge_points: List[str]
    difficulty: int = 3
    count: int = 1
    exercise_type: str = "选择题"
    model: str = DEFAULT_MODEL


class ResourceRequest(BaseModel):
    query: str
    resource_type: str = None
    difficulty: int = None
    model: str = DEFAULT_MODEL


class LearningPlanRequest(BaseModel):
    user_id: str
    knowledge_points: List[str]
    duration_days: int
    user_level: int
    model: str = DEFAULT_MODEL


class ConceptRequest(BaseModel):
    concept_name: str
    context: str = ""
    user_level: int = 3
    model: str = DEFAULT_MODEL


class SimulationRequest(BaseModel):
    topic: str
    complexity: int = 3
    model: str = DEFAULT_MODEL


# 错误处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "请求参数验证失败",
            "data": str(exc)
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    print("Error:", str(exc))
    print("Traceback:", traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "data": str(exc) if app.debug else None
        }
    )


# 重试装饰器
def with_retry(max_attempts: int = 3):
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )


# API路由
@app.get("/api/dialogue/stream")
async def handle_dialogue_stream(
    session_id: str,
    message: str,
    model: str = DEFAULT_MODEL
):
    """流式处理用户对话交互"""
    try:
        async def generate():
            async for chunk in langchain_agent.process_message(
                session_id,
                message,
                model
            ):
                if chunk:
                    # 统一使用对象格式发送
                    if isinstance(chunk, str):
                        data = {
                            "type": "chunk",
                            "content": chunk
                        }
                    else:
                        data = chunk
                    yield f"data: {json.dumps(data)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        error_msg = str(e)
        print(f"Streaming error: {error_msg}")

        async def error_response():
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            error_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )


@app.post("/api/dialogue", response_model=ResponseModel)
@with_retry()
async def handle_dialogue(request: DialogueRequest):
    """处理用户对话交互（传统方式）"""
    try:
        response = []
        async for chunk in langchain_agent.process_message(
            request.session_id,
            request.message,
            request.model
        ):
            response.append(chunk)

        return ResponseModel(
            success=True,
            message="对话处理成功",
            data={
                "session_id": request.session_id,
                "response": "".join(response),
                "model": request.model
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/api/tool_call", response_model=ResponseModel)
@with_retry()
async def handle_tool_call(request: ToolCallRequest):
    """处理工具调用"""
    try:
        response = []
        async for chunk in langchain_agent.process_message(
            "tool_session",
            f"使用{request.tool_name}工具，参数：{request.params}",
            request.model
        ):
            response.append(chunk)

        return ResponseModel(
            success=True,
            message="工具调用成功",
            data={
                "result": "".join(response),
                "model": request.model
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"工具调用失败：{str(e)}"
        )


@app.get("/api/knowledge_graph", response_model=ResponseModel)
@with_retry()
async def get_knowledge_graph(topic: str, model: str = DEFAULT_MODEL):
    """获取知识图谱数据"""
    try:
        graph_data = learning_tree_instance.get_graph_data(topic)
        return ResponseModel(
            success=True,
            message="获取知识图谱成功",
            data={
                "nodes": graph_data.get("nodes", []),
                "edges": graph_data.get("edges", []),
                "model": model
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取知识图谱失败：{str(e)}"
        )


@app.get("/api/models", response_model=ResponseModel)
@with_retry()
async def list_models():
    """获取所有可用的AI模型列表"""
    try:
        # 获取内置模型
        built_in_models = []

        # 获取Ollama模型
        ollama_models = await ollama_service.list_models()

        # 合并所有模型列表
        all_models = built_in_models + ollama_models

        return ResponseModel(
            success=True,
            message="获取模型列表成功",
            data=all_models
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取模型列表失败：{str(e)}"
        )


@app.get("/api/settings", response_model=ResponseModel)
@with_retry()
async def get_global_settings():
    """获取全局设置"""
    try:
        settings = settings_manager.load_global_settings()
        return ResponseModel(
            success=True,
            message="获取设置成功",
            data=settings
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取设置失败：{str(e)}"
        )


@app.post("/api/settings", response_model=ResponseModel)
@with_retry()
async def save_settings(settings: Settings):
    """保存用户设置"""
    try:
        updated_settings = settings_manager.update_settings(
            settings.user_id,
            settings.preferences
        )
        return ResponseModel(
            success=True,
            message="设置保存成功",
            data=updated_settings
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"设置保存失败：{str(e)}"
        )


@app.get("/api/settings/{user_id}", response_model=ResponseModel)
@with_retry()
async def get_user_settings(user_id: str):
    """获取用户设置"""
    try:
        settings = settings_manager.get_merged_settings(user_id)
        return ResponseModel(
            success=True,
            message="获取设置成功",
            data=settings
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取设置失败：{str(e)}"
        )


@app.get("/health", response_model=ResponseModel)
async def health_check():
    """健康检查"""
    return ResponseModel(
        success=True,
        message="服务正常运行",
        data={
            "status": "ok",
            "version": "0.1.0",
            "default_model": DEFAULT_MODEL,
            "base_url": DEFAULT_BASE_URL
        }
    )


# 教程管理相关路由
tutorial_manager = TutorialManager()


@app.post("/api/tutorials/save", response_model=ResponseModel)
async def save_tutorial(tutorial_data: Dict[str, Any]):
    """保存教程"""
    try:
        filename = tutorial_manager.save_tutorial(tutorial_data)
        return ResponseModel(
            success=True,
            message="教程保存成功",
            data={"filename": filename}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"保存教程失败：{str(e)}"
        )


@app.get("/api/tutorials/list", response_model=ResponseModel)
async def get_tutorial_list():
    """获取教程列表"""
    try:
        tutorials = tutorial_manager.get_tutorial_list()
        return ResponseModel(
            success=True,
            message="获取教程列表成功",
            data=tutorials
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取教程列表失败：{str(e)}"
        )


@app.get("/api/tutorials/{tutorial_id}", response_model=ResponseModel)
async def get_tutorial(tutorial_id: str):
    """获取单个教程内容"""
    try:
        tutorial = tutorial_manager.get_tutorial(tutorial_id)
        return ResponseModel(
            success=True,
            message="获取教程成功",
            data=tutorial
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取教程失败：{str(e)}"
        )


@app.delete("/api/tutorials/{tutorial_id}", response_model=ResponseModel)
async def delete_tutorial(tutorial_id: str):
    """删除教程"""
    try:
        success = tutorial_manager.delete_tutorial(tutorial_id)
        return ResponseModel(
            success=success,
            message="删除教程成功" if success else "教程不存在"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除教程失败：{str(e)}"
        )

# 知识图谱生成器
knowledge_graph_generator = KnowledgeGraphGenerator(langchain_agent.llm)


@app.post("/api/knowledge_graph/generate")
async def generate_knowledge_graph(request: Request):
    """生成知识图谱（流式输出）"""
    try:
        data = await request.json()
        topic = data.get("topic")
        description = data.get("description", "")
        
        if not topic:
            raise ValueError("主题不能为空")
        
        async def generate():
            async for chunk in knowledge_graph_generator.expand_knowledge(
                topic=topic,
                description=description
            ):
                if chunk:
                    yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        error_msg = str(e)
        print(f"Streaming error: {error_msg}")
        
        async def error_response():
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            error_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )


@app.post("/api/knowledge_graph/save")
async def save_knowledge_graph(request: Request):
    """保存知识图谱"""
    try:
        data = await request.json()
        topic = data.get("topic")
        if not topic:
            raise ValueError("主题不能为空")
            
        filename = knowledge_graph_manager.save_graph(data, topic)
        
        return ResponseModel(
            success=True,
            message="知识图谱保存成功",
            data={"filename": filename}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"保存知识图谱失败：{str(e)}"
        )


@app.get("/api/knowledge_graph/list")
async def list_knowledge_graphs():
    """获取已保存的知识图谱列表"""
    try:
        graph_list = knowledge_graph_manager.get_graph_list()
        return ResponseModel(
            success=True,
            message="获取知识图谱列表成功",
            data=graph_list
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取知识图谱列表失败：{str(e)}"
        )
    

@app.get("/api/knowledge_graph/{filename}")
async def get_knowledge_graph_data(filename: str):
    """获取指定知识图谱的数据"""
    try:
        graph_data = knowledge_graph_manager.get_graph(filename)
        return ResponseModel(
            success=True,
            message="获取知识图谱数据成功",
            data=graph_data
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"知识图谱文件 {filename} 不存在"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取知识图谱数据失败：{str(e)}"
        )


@app.delete("/api/knowledge_graph/{filename}")
async def delete_knowledge_graph(filename: str):
    """删除指定的知识图谱"""
    try:
        success = knowledge_graph_manager.delete_graph(filename)
        return ResponseModel(
            success=success,
            message="知识图谱删除成功" if success else "知识图谱不存在"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除知识图谱失败：{str(e)}"
        )


@app.post("/api/knowledge_graph/expand")
async def expand_knowledge_node(request: Request):
    """扩展知识图谱节点（流式响应）"""
    try:
        data = await request.json()
        node_id = data.get("nodeId")
        topic = data.get("topic")
        description = data.get("description", "")
        category = data.get("category", "")
        current_nodes = data.get("currentNodes", [])
        
        if not node_id or not topic:
            raise ValueError("节点ID和主题不能为空")
        
        async def generate():
            async for chunk in knowledge_graph_generator.expand_single_node(
                node_id=node_id,
                topic=topic,
                description=description,
                category=category,
                current_nodes=current_nodes
            ):
                if chunk:
                    yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        error_msg = str(e)
        print(f"扩展节点失败: {error_msg}")
        
        async def error_response():
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            error_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )


# 知识点解析相关路由
@app.post("/api/knowledge_point/parse", response_model=ResponseModel)
@with_retry()
async def parse_knowledge_point(request: KnowledgePointRequest):
    """解析知识点"""
    try:
        knowledge_point = await knowledge_point_parser.parse_knowledge_point(request.content)
        return ResponseModel(
            success=True,
            message="解析知识点成功",
            data=knowledge_point.dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"解析知识点失败：{str(e)}"
        )


# 练习题生成相关路由
@app.post("/api/exercise/generate", response_model=ResponseModel)
@with_retry()
async def generate_exercises(request: ExerciseRequest):
    """生成练习题"""
    try:
        exercises = await exercise_generator.generate_exercise_set(
            request.knowledge_points,
            request.count,
            (request.difficulty, request.difficulty)
        )
        return ResponseModel(
            success=True,
            message="生成练习题成功",
            data=[exercise.dict() for exercise in exercises]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成练习题失败：{str(e)}"
        )


# 学习资源搜索相关路由
@app.post("/api/resources/search", response_model=ResponseModel)
@with_retry()
async def search_resources(request: ResourceRequest):
    """搜索学习资源"""
    try:
        resources = await resource_searcher.search_resources(
            request.query,
            request.resource_type,
            request.difficulty
        )
        return ResponseModel(
            success=True,
            message="搜索资源成功",
            data=[resource.dict() for resource in resources]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"搜索资源失败：{str(e)}"
        )


# 学习计划生成相关路由
@app.post("/api/learning_plan/generate", response_model=ResponseModel)
@with_retry()
async def generate_learning_plan(request: LearningPlanRequest):
    """生成学习计划"""
    try:
        plan = await learning_plan_generator.generate_plan(
            request.user_id,
            request.knowledge_points,
            request.duration_days,
            request.user_level
        )
        return ResponseModel(
            success=True,
            message="生成学习计划成功",
            data=plan.dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成学习计划失败：{str(e)}"
        )


# 概念分析相关路由
@app.post("/api/concept/analyze", response_model=ResponseModel)
@with_retry()
async def analyze_concept(request: ConceptRequest):
    """分析概念"""
    try:
        concept = await concept_analyzer.analyze_concept(
            request.concept_name,
            request.context
        )
        explanation = await concept_analyzer.explain_concept(
            concept,
            request.user_level
        )
        return ResponseModel(
            success=True,
            message="分析概念成功",
            data={
                "concept": concept.dict(),
                "explanation": explanation
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分析概念失败：{str(e)}"
        )


# 仿真环境相关路由
@app.post("/api/simulation/create", response_model=ResponseModel)
@with_retry()
async def create_simulation(request: SimulationRequest):
    """创建仿真环境"""
    try:
        simulation = await simulation_builder.create_simulation(
            request.topic,
            request.complexity
        )
        return ResponseModel(
            success=True,
            message="创建仿真环境成功",
            data=simulation.dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建仿真环境失败：{str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    print("Initializing LangChain Agent...")
    langchain_agent  # 初始化agent
    print("Initializing Learning Tree...")
    learning_tree_instance  # 初始化learning tree
    print("Initializing Settings...")
    settings_manager  # 初始化settings manager
    print("Initializing Knowledge Graph Generator...")
    knowledge_graph_generator  # 初始化知识图谱生成器
    print("Initializing Tutorial Manager...")
    tutorial_manager  # 初始化tutorial manager
    print(f"Tutorial save directory: {tutorial_manager.save_dir}")
    
    # 确保保存目录存在
    os.makedirs(tutorial_manager.save_dir, exist_ok=True)

    # 设置调试模式
    app.debug = True
    
    # 配置uvicorn服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        timeout_keep_alive=TIMEOUT,
        access_log=True
    )