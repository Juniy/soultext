from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class OptimizationRun:
    timestamp: str = ""
    eval_score: float = 0.0
    eval_grade: str = ""
    weak_dimensions: List[str] = field(default_factory=list)
    suggestion: str = ""
    parameter_adjustments: Dict[str, float] = field(default_factory=dict)
    prompt_adjustments: List[str] = field(default_factory=list)
    result_text: str = ""
    result_score: float = 0.0
    improved: bool = False


class NovelOptimizer:
    """?????????????????????"""

    TARGET_GRADE = "A"  # ????
    TARGET_SCORE = 80.0  # ????

    # ??????????
    DIMENSION_PARAM_MAP = {
        "????": {"temperature": 0.05, "prompt": "???????????"},
        "????": {"temperature": 0.03, "prompt": "???????????????"},
        "????": {"temperature": -0.03, "prompt": "?????????"},
        "????": {"temperature": -0.05, "prompt": "????????????????"},
        "???": {"temperature": 0.0, "prompt": "?????????"},
        "?????": {"temperature": -0.02, "prompt": "?????????"},
        "????": {"temperature": 0.02, "prompt": "??????????"},
        "???": {"temperature": 0.08, "prompt": "???????????"},
    }

    def __init__(self, evaluator=None):
        self.evaluator = evaluator
        self.history: Dict[str, List[OptimizationRun]] = {}  # novel_id -> runs
        self.max_iterations = 5  # ????????

    def analyze_evaluation(self, eval_result: Dict) -> Dict:
        """?????????????"""
        if not eval_result or "criteria" not in eval_result:
            return {"weak": [], "suggestions": []}

        criteria = eval_result["criteria"]
        weak = []
        suggestions = []
        for dim_name, dim_data in criteria.items():
            score = dim_data.get("score", 0)
            if score < 60:
                weak.append({
                    "name": dim_data.get("name", dim_name),
                    "score": score,
                    "weight": dim_data.get("weight", 0),
                    "suggestions": dim_data.get("suggestions", [])
                })
                suggestions.extend(dim_data.get("suggestions", []))

        weak.sort(key=lambda x: x["weight"], reverse=True)
        return {
            "weak": weak,
            "suggestions": suggestions[:5],
            "overall_score": eval_result.get("overall_score", 0),
            "grade": eval_result.get("grade", "F"),
        }

    def generate_adjustments(self, analysis: Dict, current_settings: Optional[Dict] = None) -> Dict:
        """??????????????"""
        settings = dict(current_settings or {})
        prompt_adj = []
        temp_adj = 0.0

        for weak_dim in analysis.get("weak", []):
            dim_name = weak_dim["name"]
            param_map = self.DIMENSION_PARAM_MAP.get(dim_name, {})

            # ????
            if "temperature" in param_map:
                temp_adj += param_map["temperature"]

            # Prompt??
            if "prompt" in param_map:
                prompt_adj.append(f"[{dim_name}]: {param_map['prompt']}")

            # ??????
            for s in weak_dim.get("suggestions", []):
                prompt_adj.append(f"[??]: {s}")

        # ??????
        if temp_adj != 0:
            current_temp = float(settings.get("temperature", 0.8))
            settings["temperature"] = max(0.1, min(1.5, current_temp + temp_adj))

        if prompt_adj:
            current_custom = settings.get("custom_instructions", "")
            adj_text = "; ".join(prompt_adj[:3])
            settings["custom_instructions"] = (current_custom + "\n[????]: " + adj_text).strip()

        return {
            "settings": settings,
            "prompt_adjustments": prompt_adj[:5],
            "temperature_adjustment": round(temp_adj, 3),
            "adjustment_summary": "?".join([w["name"] for w in analysis.get("weak", [])]) if analysis.get("weak") else "??????",
        }

    def is_target_achieved(self, eval_result: Dict) -> bool:
        """????????"""
        score = eval_result.get("overall_score", 0) if eval_result else 0
        return score >= self.TARGET_SCORE

    def record_run(self, novel_id: str, run: OptimizationRun):
        """????????"""
        if novel_id not in self.history:
            self.history[novel_id] = []
        self.history[novel_id].append(run)

    def get_optimization_history(self, novel_id: str) -> List[Dict]:
        """??????"""
        runs = self.history.get(novel_id, [])
        return [
            {
                "timestamp": r.timestamp,
                "eval_score": r.eval_score,
                "eval_grade": r.eval_grade,
                "weak_dimensions": r.weak_dimensions,
                "improved": r.improved,
                "suggestion": r.suggestion,
            }
            for r in runs
        ]

    def get_optimization_status(self, novel_id: str) -> Dict:
        """????????"""
        runs = self.history.get(novel_id, [])
        if not runs:
            return {"status": "???", "iterations": 0}

        last = runs[-1]
        improvements = [r for r in runs if r.improved]
        score_trend = [r.eval_score for r in runs]

        return {
            "status": "????" if last.eval_score >= self.TARGET_SCORE else "???",
            "iterations": len(runs),
            "current_score": last.eval_score,
            "current_grade": last.eval_grade,
            "best_score": max(score_trend) if score_trend else 0,
            "improvements": len(improvements),
            "score_trend": score_trend,
            "target_score": self.TARGET_SCORE,
            "target_grade": self.TARGET_GRADE,
            "remaining_gap": max(0, self.TARGET_SCORE - last.eval_score),
        }
