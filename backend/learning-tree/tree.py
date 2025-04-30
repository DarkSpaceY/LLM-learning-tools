from typing import List, Dict, Any
import json
import os

class LearningTree:
    def __init__(self, save_dir: str = "Saves"):
        self.nodes = []
        self.edges = []
        self.save_dir = save_dir
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        # TODO: Implement loading from a persistent store if needed
        print("Initializing Learning Tree...")

    def get_graph_data(self, topic: str) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieves nodes and edges relevant to a specific topic."""
        # TODO: Implement logic to filter/retrieve graph data based on the topic
        print(f"Retrieving graph data for topic: {topic}")
        # Placeholder: return the entire graph for now
        return {"nodes": self.nodes, "edges": self.edges}

    def add_node(self, node_id: str, data: Dict[str, Any]):
        """Adds a node to the learning tree."""
        # TODO: Add validation and prevent duplicates
        self.nodes.append({"id": node_id, **data})
        print(f"Added node: {node_id}")

    def add_edge(self, source_id: str, target_id: str, data: Dict[str, Any]):
        """Adds an edge between two nodes."""
        # TODO: Add validation (ensure nodes exist)
        self.edges.append({"source": source_id, "target": target_id, **data})
        print(f"Added edge: {source_id} -> {target_id}")

    def save_tree(self, filename: str = "learning_tree.json"):
        """Saves the current tree structure to a file."""
        save_path = os.path.join(self.save_dir, filename)
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump({"nodes": self.nodes, "edges": self.edges}, f, indent=4)
            print(f"Learning tree saved to {save_path}")
        except IOError as e:
            print(f"Error saving learning tree: {e}")

    def load_tree(self, filename: str = "learning_tree.json"):
        """Loads the tree structure from a file."""
        load_path = os.path.join(self.save_dir, filename)
        try:
            if os.path.exists(load_path):
                with open(load_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.nodes = data.get("nodes", [])
                    self.edges = data.get("edges", [])
                print(f"Learning tree loaded from {load_path}")
            else:
                print(f"Save file not found: {load_path}. Starting with an empty tree.")
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading learning tree: {e}. Starting with an empty tree.")
            self.nodes = []
            self.edges = []

# Instantiate the learning tree (or manage instances as needed)
learning_tree_instance = LearningTree()
# Attempt to load existing data on startup
learning_tree_instance.load_tree()