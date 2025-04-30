import os
import json
import datetime
from typing import List, Dict, Any


class KnowledgeGraphManager:
    def __init__(self):
        self.save_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'mapSaves'
        )
        os.makedirs(self.save_dir, exist_ok=True)

    def save_graph(self, graph_data: Dict[str, Any], topic: str) -> str:
        """保存知识图谱到文件"""
        # 生成文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{topic}.json"
        filepath = os.path.join(self.save_dir, filename)

        # 保存数据
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)

        return filename

    def get_graph_list(self) -> List[Dict[str, Any]]:
        """获取已保存的知识图谱列表"""
        graph_files = []
        for filename in os.listdir(self.save_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.save_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    # 提取主题和时间戳
                    timestamp = filename.split('_')[0]
                    datetime_obj = datetime.datetime.strptime(timestamp, "%Y%m%d")
                    graph_files.append({
                        'filename': filename,
                        'topic': data.get('metadata', {}).get('topic', '未知主题'),
                        'created_at': datetime_obj.isoformat(),
                        'node_count': len(data.get('nodes', [])),
                        'edge_count': len(data.get('edges', []))
                    })
                except Exception as e:
                    print(f"Error loading graph file {filename}: {e}")
                    continue

        return sorted(graph_files, key=lambda x: x['created_at'], reverse=True)

    def get_graph(self, filename: str) -> Dict[str, Any]:
        """获取指定的知识图谱数据"""
        filepath = os.path.join(self.save_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"知识图谱文件 {filename} 不存在")

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def delete_graph(self, filename: str) -> bool:
        """删除指定的知识图谱文件"""
        filepath = os.path.join(self.save_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False