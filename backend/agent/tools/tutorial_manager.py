import os
import json
from datetime import datetime
from typing import List, Dict, Any
import sys

class TutorialManager:
    def __init__(self, save_dir: str = None):
        """初始化教程管理器"""
        self.save_dir = 'Saves'
        os.makedirs(self.save_dir, exist_ok=True)

    def save_tutorial(self, tutorial_data: Dict[str, Any]) -> str:
        """保存教程到文件"""
        try:
            # 创建文件名（使用时间戳和标题）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_title = "".join(x for x in tutorial_data['title'] if x.isalnum() or x in (' ', '-', '_'))
            filename = f"{timestamp}_{safe_title[:30]}.json"
            filepath = os.path.join(self.save_dir, filename)

            # 添加元数据
            tutorial_data['metadata'] = {
                'created_at': datetime.now().isoformat(),
                'filename': filename
            }

            # 保存到文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(tutorial_data, f, ensure_ascii=False, indent=2)

            return filename

        except Exception as e:
            raise Exception(f"Failed to save tutorial: {str(e)}")

    def get_tutorial_list(self) -> List[Dict[str, Any]]:
        """获取所有保存的教程列表"""
        tutorials = []
        try:
            # 遍历保存目录中的所有 json 文件
            for filename in os.listdir(self.save_dir):
                if not filename.endswith('.json'):
                    continue

                filepath = os.path.join(self.save_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    tutorial = json.load(f)

                # 转换为树形结构
                try:
                    tree_data = self._convert_to_tree(tutorial)
                except Exception as e:
                    print(f"Failed to convert tutorial {filename} to tree: {str(e)}")
                    continue
                tutorials.append(tree_data)

            # 按创建时间倒序排序
            tutorials.sort(key=lambda x: x['metadata']['created_at'], reverse=True)
            return tutorials

        except Exception as e:
            raise Exception(f"Failed to get tutorial list: {str(e)}")

    def _convert_to_tree(self, tutorial: Dict[str, Any]) -> Dict[str, Any]:
        """将教程数据转换为树形结构"""
        tree = {
            'id': tutorial['metadata']['filename'],
            'label': tutorial['title'],
            'type': 'tutorial',
            'metadata': tutorial['metadata'],
            'children': []
        }

        # 添加章节
        for chapter in tutorial['chapters']:
            chapter_node = {
                'id': f"chapter-{chapter['number']}",
                'label': f"{chapter['number']}. {chapter['title']}",
                'type': 'chapter',
                'description': chapter['description'],
                'children': []
            }

            # 添加小节
            for section in chapter['sections']:
                section_node = {
                    'id': f"section-{section['number']}",
                    'label': f"{section['number']} {section['title']}",
                    'type': 'section',
                    'title': f"{section['number']} {section['title']}",
                    'description': section['description'],
                    'content': section['content']
                }
                chapter_node['children'].append(section_node)

            tree['children'].append(chapter_node)

        return tree

    def get_tutorial(self, tutorial_id: str) -> Dict[str, Any]:
        """获取指定教程的完整内容"""
        try:
            filepath = os.path.join(self.save_dir, tutorial_id)
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Tutorial not found: {tutorial_id}")

            with open(filepath, 'r', encoding='utf-8') as f:
                tutorial = json.load(f)
                return self._convert_to_tree(tutorial)

        except Exception as e:
            raise Exception(f"Failed to get tutorial: {str(e)}")

    def delete_tutorial(self, tutorial_id: str) -> bool:
        """删除指定的教程"""
        try:
            filepath = os.path.join(self.save_dir, tutorial_id)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            raise Exception(f"Failed to delete tutorial: {str(e)}")