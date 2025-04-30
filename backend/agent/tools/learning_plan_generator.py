from typing import List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from langchain.llms.base import BaseLLM

class LearningTask(BaseModel):
    """学习任务数据模型"""
    id: str
    title: str
    description: str
    knowledge_points: List[str]  # 相关知识点ID列表
    estimated_time: int  # 预计完成时间（分钟）
    difficulty: int  # 1-5表示难度等级
    resources: List[Dict[str, str]]  # 学习资源列表
    exercises: List[str]  # 练习题ID列表
    status: str = "pending"  # pending, in_progress, completed
    progress: float = 0.0  # 完成进度（0-1）

class LearningPlan(BaseModel):
    """学习计划数据模型"""
    id: str
    user_id: str
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    tasks: List[LearningTask]
    total_time: int  # 总计划时间（分钟）
    progress: float = 0.0  # 总体进度
    status: str = "active"  # active, completed, archived

class LearningPlanGenerator:
    """学习计划生成器"""
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    async def generate_plan(self, user_id: str, knowledge_points: List[str], duration_days: int, user_level: int) -> LearningPlan:
        """生成学习计划"""
        prompt = f"""请根据以下条件生成一个学习计划：
        知识点：{', '.join(knowledge_points)}
        计划天数：{duration_days}
        用户水平：{user_level}（1-5）
        
        请生成一个合理的学习计划，包括每天的学习任务和时间安排。
        """
        
        try:
            response = await self.llm.agenerate([prompt])
            result = response.generations[0][0].text
            
            # 生成计划的起止时间
            start_date = datetime.now()
            end_date = start_date + timedelta(days=duration_days)
            
            # 生成任务列表
            tasks = []
            total_time = 0
            
            # 这里应该解析LLM的响应来生成实际的任务
            # 当前使用示例任务
            for i, kp in enumerate(knowledge_points):
                task = LearningTask(
                    id=f"task_{i}",
                    title=f"学习{kp}",
                    description=f"深入学习{kp}的核心概念和应用",
                    knowledge_points=[kp],
                    estimated_time=120,  # 2小时
                    difficulty=user_level,
                    resources=[],
                    exercises=[]
                )
                tasks.append(task)
                total_time += task.estimated_time
            
            # 创建学习计划
            plan = LearningPlan(
                id=f"plan_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                user_id=user_id,
                title=f"学习计划 - {', '.join(knowledge_points)}",
                description="自动生成的学习计划",
                start_date=start_date,
                end_date=end_date,
                tasks=tasks,
                total_time=total_time
            )
            
            return plan
        except Exception as e:
            raise ValueError(f"生成学习计划失败：{str(e)}")

    async def adjust_plan(self, plan: LearningPlan, feedback: Dict[str, Any]) -> LearningPlan:
        """根据反馈调整学习计划"""
        prompt = f"""请根据以下反馈调整学习计划：
        当前计划：{plan.title}
        计划描述：{plan.description}
        用户反馈：{feedback}
        
        请提供调整建议。
        """
        
        try:
            response = await self.llm.agenerate([prompt])
            suggestions = response.generations[0][0].text
            
            # 根据反馈调整计划
            # 这里应该实现实际的调整逻辑
            if 'extend_days' in feedback:
                plan.end_date += timedelta(days=feedback['extend_days'])
            
            if 'task_adjustments' in feedback:
                for task_id, adjustment in feedback['task_adjustments'].items():
                    for task in plan.tasks:
                        if task.id == task_id:
                            if 'estimated_time' in adjustment:
                                task.estimated_time = adjustment['estimated_time']
                            if 'difficulty' in adjustment:
                                task.difficulty = adjustment['difficulty']
            
            # 重新计算总时间
            plan.total_time = sum(task.estimated_time for task in plan.tasks)
            
            return plan
        except Exception as e:
            raise ValueError(f"调整学习计划失败：{str(e)}")

    async def track_progress(self, plan: LearningPlan, task_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """跟踪学习计划进度"""
        try:
            # 更新任务进度
            for update in task_updates:
                task_id = update.get('task_id')
                progress = update.get('progress', 0)
                status = update.get('status', 'pending')
                
                for task in plan.tasks:
                    if task.id == task_id:
                        task.progress = progress
                        task.status = status
            
            # 计算总体进度
            completed_tasks = sum(1 for task in plan.tasks if task.status == 'completed')
            plan.progress = completed_tasks / len(plan.tasks) if plan.tasks else 0
            
            # 检查是否完成所有任务
            if plan.progress >= 1.0:
                plan.status = 'completed'
            
            return {
                'plan_id': plan.id,
                'progress': plan.progress,
                'status': plan.status,
                'completed_tasks': completed_tasks,
                'total_tasks': len(plan.tasks)
            }
        except Exception as e:
            raise ValueError(f"跟踪进度失败：{str(e)}")

    async def generate_progress_report(self, plan: LearningPlan) -> Dict[str, Any]:
        """生成学习进度报告"""
        try:
            completed_tasks = [task for task in plan.tasks if task.status == 'completed']
            in_progress_tasks = [task for task in plan.tasks if task.status == 'in_progress']
            pending_tasks = [task for task in plan.tasks if task.status == 'pending']
            
            # 计算时间统计
            total_time_spent = sum(task.estimated_time * task.progress for task in plan.tasks)
            remaining_time = sum(task.estimated_time * (1 - task.progress) for task in plan.tasks)
            
            return {
                'plan_id': plan.id,
                'overall_progress': plan.progress,
                'status': plan.status,
                'time_statistics': {
                    'total_time_spent': total_time_spent,
                    'remaining_time': remaining_time,
                    'total_planned_time': plan.total_time
                },
                'task_statistics': {
                    'completed': len(completed_tasks),
                    'in_progress': len(in_progress_tasks),
                    'pending': len(pending_tasks),
                    'total': len(plan.tasks)
                },
                'completed_tasks': [
                    {
                        'id': task.id,
                        'title': task.title,
                        'time_spent': task.estimated_time * task.progress
                    } for task in completed_tasks
                ],
                'next_tasks': [
                    {
                        'id': task.id,
                        'title': task.title,
                        'estimated_time': task.estimated_time
                    } for task in pending_tasks[:3]  # 下一步要完成的任务
                ]
            }
        except Exception as e:
            raise ValueError(f"生成进度报告失败：{str(e)}")