import json, os
from typing import Dict, List, Optional, Any
from datetime import datetime
import networkx as nx

class NovelGraphStore:
    NODE_TYPES = ["character", "location", "scene", "chapter", "event", "world_item", "timeline_era"]

    def __init__(self, storage_path: str = None):
        self.graph = nx.MultiDiGraph()
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "novel_graph.json"
        )
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

    def add_node(self, node_id: str, node_type: str, **attrs) -> bool:
        if node_type not in self.NODE_TYPES:
            raise ValueError(f"Invalid node type: {node_type}")
        attrs["node_type"] = node_type
        attrs["created_at"] = attrs.get("created_at", datetime.now().isoformat())
        self.graph.add_node(node_id, **attrs)
        return True

    def add_edge(self, source: str, target: str, edge_type: str, **attrs) -> bool:
        if source not in self.graph or target not in self.graph:
            raise ValueError(f"Node not found: {source} or {target}")
        attrs["edge_type"] = edge_type
        self.graph.add_edge(source, target, key=edge_type, **attrs)
        return True

    def get_node(self, node_id: str) -> Optional[Dict]:
        if node_id not in self.graph:
            return None
        data = dict(self.graph.nodes[node_id])
        data["id"] = node_id
        return data

    def get_connections(self, node_id: str, max_depth: int = 2) -> Dict:
        if node_id not in self.graph:
            return {}
        connections = {"nodes": {}, "edges": []}
        visited = set()
        queue = [(node_id, 0)]
        while queue and len(visited) < 200:
            current, depth = queue.pop(0)
            if current in visited or depth > max_depth:
                continue
            visited.add(current)
            nd = dict(self.graph.nodes[current])
            nd["id"] = current
            connections["nodes"][current] = nd
            for nb in self.graph.neighbors(current):
                ed = self.graph.get_edge_data(current, nb)
                if ed:
                    for k, d in ed.items():
                        connections["edges"].append({"source": current, "target": nb, "type": d.get("edge_type", k)})
                if nb not in visited and depth + 1 <= max_depth:
                    queue.append((nb, depth + 1))
            for pr in self.graph.predecessors(current):
                ed = self.graph.get_edge_data(pr, current)
                if ed:
                    for k, d in ed.items():
                        connections["edges"].append({"source": pr, "target": current, "type": d.get("edge_type", k)})
                if pr not in visited and depth + 1 <= max_depth:
                    queue.append((pr, depth + 1))
        return connections

    def get_character_network(self, novel_id: str) -> Dict:
        chars = {}
        for nid, data in self.graph.nodes(data=True):
            if data.get("novel_id") == novel_id and data.get("node_type") == "character":
                chars[nid] = dict(data)
        rels = []
        for u, v, k, data in self.graph.edges(keys=True, data=True):
            if u in chars and v in chars:
                rels.append({"source": u, "target": v, "type": data.get("edge_type", k)})
        return {"characters": chars, "relationships": rels}

    def get_timeline_events(self, novel_id: str) -> List[Dict]:
        events = []
        for nid, data in self.graph.nodes(data=True):
            if data.get("novel_id") == novel_id and data.get("node_type") == "event":
                e = dict(data)
                e["id"] = nid
                events.append(e)
        return sorted(events, key=lambda e: e.get("timestamp", ""))

    def get_scene_sequence(self, novel_id: str) -> List[Dict]:
        scenes = []
        for nid, data in self.graph.nodes(data=True):
            if data.get("novel_id") == novel_id and data.get("node_type") == "scene":
                s = dict(data)
                s["id"] = nid
                scenes.append(s)
        return sorted(scenes, key=lambda s: (s.get("chapter_index", 9999), s.get("scene_index", 9999)))

    def get_consistency_issues(self, novel_id: str) -> List[Dict]:
        issues = []
        chars = {}
        for nid, data in self.graph.nodes(data=True):
            if data.get("novel_id") == novel_id and data.get("node_type") == "character":
                chars[nid] = dict(data)
        for cid, cd in chars.items():
            name = cd.get("name", cid)
            tags = set(cd.get("tags", []))
            for oid, od in chars.items():
                if oid >= cid:
                    continue
                otags = set(od.get("tags", []))
                if tags and otags and tags == otags:
                    issues.append({"severity": "warning", "type": "duplicate_personality",
                                   "message": f"{name} 和 {od.get('name', oid)} 性格标签完全一致",
                                   "nodes": [cid, oid]})
            rels = list(self.graph.edges(cid, keys=True, data=True))
            if len(rels) == 0:
                issues.append({"severity": "info", "type": "isolated_character",
                               "message": f"{name} 无任何关系", "nodes": [cid]})
        return issues

    def get_statistics(self) -> Dict:
        return {"total_nodes": self.graph.number_of_nodes(), "total_edges": self.graph.number_of_edges(),
                "node_types": {t: sum(1 for _, d in self.graph.nodes(data=True) if d.get("node_type") == t) for t in self.NODE_TYPES}}

    def save(self, path=None):
        with open(path or self.storage_path, "w", encoding="utf-8") as f:
            json.dump(nx.node_link_data(self.graph), f, ensure_ascii=False, indent=2)

    def load(self, path=None):
        p = path or self.storage_path
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                self.graph = nx.node_link_graph(json.load(f), directed=True, multigraph=True)

    def search(self, query: str, node_type: Optional[str] = None) -> List[Dict]:
        q = query.lower()
        res = []
        for nid, data in self.graph.nodes(data=True):
            if node_type and data.get("node_type") != node_type:
                continue
            if q in nid.lower() or any(q in str(data.get(k, "")).lower() for k in ["name", "title", "description"]):
                res.append({"id": nid, **dict(data)})
        return res[:50]
