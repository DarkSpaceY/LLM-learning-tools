from typing import List, Dict, Any
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
import re


class KnowledgePointParser:
    def __init__(self, llm: LLM):
        self.llm = llm
        
        self.prompt = PromptTemplate(
            template=(
                "请分析以下文本，提取所有关键知识点。\n\n"
                "文本内容：{text}\n\n"
                "要求：\n"
                "1. 提取所有核心知识点\n"
                "2. 为每个知识点生成100字左右的摘要\n"
                "3. 标注重要程度(high/medium/low)\n"
                "4. 列出相关概念\n"
                "5. 指出前置知识\n"
                "6. 评估难度级别(basic/intermediate/advanced)\n"
                "7. 提供2-3个示例\n"
                "8. 提取3-5个关键要点\n\n"
                "对于长文本(>1000字)，请分段处理并合并结果。\n\n"
                "请按以下XML标签格式输出，可以包含多个知识点：\n"
                "<知识点列表>\n"
                "<知识点>\n"
                "  <内容>知识点内容</内容>\n"
                "  <重要程度>high/medium/low</重要程度>\n"
                "  <相关概念>\n    - 概念1\n    - 概念2\n  </相关概念>\n"
                "  <前置知识>\n    - 知识1\n    - 知识2\n  </前置知识>\n"
                "  <难度级别>basic/intermediate/advanced</难度级别>\n"
                "  <摘要>100字左右的摘要</摘要>\n"
                "  <示例>\n    - 示例1\n    - 示例2\n  </示例>\n"
                "  <关键要点>\n    - 要点1\n    - 要点2\n    - 要点3\n  </关键要点>\n"
                "</知识点>\n"
                "</知识点列表>\n"
            ),
            input_variables=["text"]
        )

    def _parse_list_items(self, text: str) -> List[str]:
        """解析列表项，去除前导符号并清理空白"""
        items = [line.strip('- ').strip() for line in text.strip().split('\n')]
        return [item for item in items if item]

    async def parse_knowledge_point(self, text: str) -> Dict[str, Any]:
        """解析文本中的知识点"""
        try:
            # 生成并格式化提示
            prompt = self.prompt.format(text=text)
            output = []
            async for chunk in self.llm._call(prompt):
                output.append(chunk)
            output = ''.join(output)

            # 使用正则表达式提取所有知识点
            knowledge_points = []
            knowledge_point_matches = re.finditer(r'<知识点>(.*?)</知识点>', output, re.DOTALL)
            
            for kp_match in knowledge_point_matches:
                kp_content = kp_match.group(1)
                
                # 提取每个知识点的详细信息
                content_match = re.search(r'<内容>(.*?)</内容>', kp_content, re.DOTALL)
                importance_match = re.search(r'<重要程度>(.*?)</重要程度>', kp_content, re.DOTALL)
                concepts_match = re.search(r'<相关概念>(.*?)</相关概念>', kp_content, re.DOTALL)
                prereq_match = re.search(r'<前置知识>(.*?)</前置知识>', kp_content, re.DOTALL)
                difficulty_match = re.search(r'<难度级别>(.*?)</难度级别>', kp_content, re.DOTALL)
                summary_match = re.search(r'<摘要>(.*?)</摘要>', kp_content, re.DOTALL)
                examples_match = re.search(r'<示例>(.*?)</示例>', kp_content, re.DOTALL)
                points_match = re.search(r'<关键要点>(.*?)</关键要点>', kp_content, re.DOTALL)

                # 构建单个知识点字典
                knowledge_point = {
                    "content": content_match.group(1).strip() if content_match else "解析失败",
                    "importance": importance_match.group(1).strip() if importance_match else "low",
                    "related_concepts": self._parse_list_items(concepts_match.group(1)) if concepts_match else [],
                    "prerequisites": self._parse_list_items(prereq_match.group(1)) if prereq_match else [],
                    "difficulty": difficulty_match.group(1).strip() if difficulty_match else "basic",
                    "summary": summary_match.group(1).strip() if summary_match else "",
                    "examples": self._parse_list_items(examples_match.group(1)) if examples_match else [],
                    "key_points": self._parse_list_items(points_match.group(1)) if points_match else []
                }
                
                knowledge_points.append(knowledge_point)
            
            # 返回结果
            return {
                "knowledge_points": knowledge_points,
                "metadata": {
                    "text_length": len(text),
                    "success": True,
                    "count": len(knowledge_points)
                }
            }
        except Exception as e:
            print(f"知识点解析失败: {str(e)}")
            return {
                "knowledge_points": [],
                "metadata": {
                    "text_length": len(text),
                    "success": False,
                    "error": str(e),
                    "count": 0
                }
            }