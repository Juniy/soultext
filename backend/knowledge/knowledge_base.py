from typing import Dict, List, Optional
from dataclasses import dataclass, field
import os, re


@dataclass
class WritingTechnique:
    id: str
    title: str
    category: str
    summary: str
    key_points: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    prompt_template: Optional[str] = None


class KnowledgeBase:
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "doc"
        )
        self.techniques: Dict[str, WritingTechnique] = {}
        self._load_from_doc()

    def _load_from_doc(self):
        if not os.path.isdir(self.base_path):
            print(f"Doc folder not found: {self.base_path}, using fallback")
            self._load_fallback()
            return
        count = 0
        for root, dirs, files in os.walk(self.base_path):
            category = os.path.basename(root)
            if root == self.base_path:
                continue
            for fname in sorted(files):
                if not fname.endswith(".md"):
                    continue
                filepath = os.path.join(root, fname)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    tech = self._parse_technique(content, category, fname)
                    if tech:
                        self.techniques[tech.id] = tech
                        count += 1
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")
        if count == 0:
            print("No techniques loaded from doc, using fallback")
            self._load_fallback()
        else:
            print(f"Loaded {count} writing techniques from doc folder")

    def _parse_technique(self, content: str, category: str, fname: str):
        lines = content.strip().split("\n")
        title = ""
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break
        if not title:
            title = fname.replace(".md", "").replace("-", " ").strip()
        tech_id = f"tech_{category}_{fname.replace('.md','')}"
        summary = ""
        in_summary = False
        for line in lines:
            sline = line.strip()
            if sline.startswith("# "):
                in_summary = True
                continue
            if in_summary and sline and not sline.startswith("#"):
                summary = sline[:200]
                break
        key_points = []
        for line in lines:
            sline = line.strip()
            if sline.startswith("- **") or sline.startswith("- "):
                p = re.sub(r"^-\s*\*{0,2}", "", sline)
                p = re.sub(r"\*{0,2}$", "", p)
                if len(p) > 5 and len(p) < 100:
                    key_points.append(p)
        examples = []
        in_code = False
        code_block = ""
        for line in lines:
            if line.startswith("```"):
                if in_code:
                    examples.append(code_block.strip())
                    code_block = ""
                    in_code = False
                else:
                    in_code = True
            elif in_code:
                code_block += line + "\n"
        prompt = self._gen_prompt_template(title, category, summary, key_points)
        return WritingTechnique(
            id=tech_id, title=title, category=category,
            summary=summary or title, key_points=key_points[:10],
            examples=examples[:3], prompt_template=prompt
        )

    def _gen_prompt_template(self, title: str, category: str, summary: str, key_points: list):
        lines_p = [f"???? - {title}", f"??: {category}"]
        if summary:
            lines_p.append(f"??: {summary}")
        if key_points:
            lines_p.append("??:")
            for kp in key_points[:5]:
                lines_p.append(f"  - {kp}")
        return "\n".join(lines_p)

    def _load_fallback(self):
        self.techniques["emotional_core"] = WritingTechnique(
            "emotional_core", "????????", "????",
            "???? x ???? x ???? = ???????",
            ["??????????", "?????????", "?????????"],
            prompt_template="????: 1) ?????? 2) ??????? 3) ??????"
        )

    def get_all_categories(self):
        cats = {}
        for t in self.techniques.values():
            if t.category not in cats:
                cats[t.category] = []
            cats[t.category].append(t)
        return cats

    def get_prompt_enhancements(self, stage: str) -> List[str]:
        kw_map = {
            "outline": ["??", "??", "??", "???", "??"],
            "chapter": ["??", "??", "??", "??", "??"],
            "revision": ["??", "??", "??"],
        }
        kw = kw_map.get(stage, [])
        result = []
        for t in self.techniques.values():
            if t.prompt_template and any(k in t.title for k in kw):
                result.append(t.prompt_template)
                if len(result) >= 5:
                    break
        return result

    def search(self, q: str) -> List[WritingTechnique]:
        q = q.lower()
        return [t for t in self.techniques.values()
                if q in t.title.lower() or q in t.category.lower() or q in t.summary.lower()]

    def get_statistics(self) -> Dict:
        cats = self.get_all_categories()
        return {
            "total": len(self.techniques),
            "categories": len(cats),
            "with_prompt": sum(1 for t in self.techniques.values() if t.prompt_template),
        }
