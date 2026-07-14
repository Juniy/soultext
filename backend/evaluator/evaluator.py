from typing import Dict, List, Optional
from dataclasses import dataclass, field
import re

@dataclass
class EvalCriterion:
    name: str; weight: float; score: float = 0.0
    details: str = ""; suggestions: List[str] = field(default_factory=list)

@dataclass
class EvalResult:
    overall_score: float = 0.0
    criteria: Dict[str, EvalCriterion] = field(default_factory=dict)
    summary: str = ""; grade: str = "未评级"

    def to_dict(self) -> Dict:
        return {"overall_score": round(self.overall_score, 1), "grade": self.grade, "summary": self.summary,
                "criteria": {k: {"name": v.name, "weight": v.weight, "score": round(v.score, 1),
                                 "details": v.details, "suggestions": v.suggestions[:3]} for k, v in self.criteria.items()}}

class NovelEvaluator:
    def __init__(self):
        self.dims = {
            "emotional_resonance": {"name": "情感共鸣", "weight": 0.18, "desc": "能否引起情感共鸣"},
            "character_depth": {"name": "人物塑造", "weight": 0.17, "desc": "角色是否立体鲜活"},
            "plot_quality": {"name": "情节设计", "weight": 0.15, "desc": "情节是否紧凑合理"},
            "writing_style": {"name": "文笔技巧", "weight": 0.12, "desc": "语言是否精准优美"},
            "world_building": {"name": "世界观", "weight": 0.12, "desc": "世界观是否完整自洽"},
            "consistency": {"name": "前后一致性", "weight": 0.10, "desc": "是否前后矛盾"},
            "pacing": {"name": "节奏控制", "weight": 0.08, "desc": "节奏是否张弛有度"},
            "originality": {"name": "创新性", "weight": 0.08, "desc": "是否有独特创意"},
        }

    def evaluate(self, text: str, ctx: Optional[Dict] = None) -> EvalResult:
        r = EvalResult()
        r.criteria = {k: EvalCriterion(name=v["name"], weight=v["weight"]) for k, v in self.dims.items()}
        if not text or len(text.strip()) < 50:
            for k in r.criteria: r.criteria[k].score, r.criteria[k].details = 0, "文本过短"
            r.overall_score, r.grade, r.summary = 0, "无内容", "文本太短"
            return r
        self._eval_emotion(text, r.criteria["emotional_resonance"])
        self._eval_character(text, r.criteria["character_depth"])
        self._eval_plot(text, r.criteria["plot_quality"])
        self._eval_style(text, r.criteria["writing_style"])
        self._eval_pacing(text, r.criteria["pacing"])
        self._eval_originality(text, r.criteria["originality"])
        if ctx:
            r.criteria["world_building"].score = 70
            r.criteria["consistency"].score = 70
        tw = sum(c.weight for c in r.criteria.values())
        r.overall_score = sum(c.score * c.weight for c in r.criteria.values()) / tw if tw > 0 else 0
        r.grade = self._grade(r.overall_score)
        r.summary = self._summary(r)
        return r

    def _eval_emotion(self, t: str, c: EvalCriterion):
        s = 50.0; d, sg = [], []
        ew = ["心痛","泪水","颤抖","哽咽","沉默","温暖","孤独","绝望","希望","愤怒","悲伤","喜悦","恐惧","爱","恨","思念","遗憾","愧疚"]
        cnt = sum(1 for w in ew if w in t)
        if cnt >= 10: s += 20; d.append("情感词汇丰富")
        elif cnt >= 5: s += 10; d.append("有一定情感表达")
        else: s -= 10; sg.append("增加情感词汇")
        if any(p in t for p in ["感觉","闻到","听到","看到","触摸"]): s += 10; d.append("有感官细节")
        else: sg.append("增加五感描写")
        if any(m in t for m in ["心想","想道","内心","心里"]): s += 10; d.append("有内心独白")
        else: sg.append("增加内心独白")
        c.score = max(0, min(100, s)); c.details = "; ".join(d) or "情感表达不充分"; c.suggestions = sg

    def _eval_character(self, t: str, c: EvalCriterion):
        s = 50.0; d, sg = [], []
        dc = sum(1 for m in ["说","道","问","答","喊","叫","吼"] if m in t)
        if dc >= 20: s += 15; d.append("对话丰富")
        elif dc >= 10: s += 8; d.append("有一定对话")
        else: s -= 10; sg.append("增加对话描写")
        if any(w in t for w in ["矛盾","纠结","犹豫","挣扎","抉择","两难"]): s += 15; d.append("展现内心矛盾")
        else: sg.append("让角色面临两难抉择")
        c.score = max(0, min(100, s)); c.details = "; ".join(d) or "人物塑造不够立体"; c.suggestions = sg

    def _eval_plot(self, t: str, c: EvalCriterion):
        s = 50.0; d, sg = [], []
        tw = ["突然","然而","但是","不料","危机","冲突","转折","意外","真相"]
        if sum(1 for w in tw if w in t) >= 8: s += 20; d.append("情节张力充足")
        elif sum(1 for w in tw if w in t) >= 4: s += 10
        else: sg.append("增加情节冲突")
        if any(m in t for m in ["为什么","怎么回事","秘密","谜","真相","难道"]): s += 15; d.append("有悬疑元素")
        else: sg.append("设置悬念钩子")
        if any(f in t for f in ["后来","回想","预兆","预感","注定","仿佛"]): s += 10; d.append("有伏笔")
        else: sg.append("埋设伏笔")
        c.score = max(0, min(100, s)); c.details = "; ".join(d) or "情节设计平淡"; c.suggestions = sg

    def _eval_style(self, t: str, c: EvalCriterion):
        s = 60.0; d, sg = [], []
        sts = re.split(r"[。！？；]", t)
        if len(sts) > 5:
            avg = sum(len(x) for x in sts) / len(sts)
            if 15 <= avg <= 40: s += 10; d.append(f"句子长短适中(均{avg:.0f}字)")
            elif avg > 60: s -= 5; sg.append("长句需拆分")
        for dv in ["比喻","拟人","排比","对比","象征"]:
            if dv in t: s += 3; d.append(f"用了{dv}")
        c.score = max(0, min(100, s)); c.details = "; ".join(d) or "文笔普通"; c.suggestions = sg

    def _eval_pacing(self, t: str, c: EvalCriterion):
        s = 60.0; d, sg = [], []
        pars = t.split("\n\n")
        if len(pars) >= 3:
            avg = sum(len(p) for p in pars) / len(pars)
            if 50 <= avg <= 200: s += 15; d.append(f"段落适中(均{avg:.0f}字)")
            elif avg > 300: s -= 5; sg.append("段落过长")
        c.score = max(0, min(100, s)); c.details = "; ".join(d) or "节奏一般"; c.suggestions = sg

    def _eval_originality(self, t: str, c: EvalCriterion):
        s = 60.0; d = []
        if any(u in t for u in ["从未想过","与众不同","独特","罕见","新奇"]): s += 15; d.append("有独特视角")
        if len(re.findall(r"像[， ]", t)) >= 3: s += 10; d.append("比喻新颖")
        c.score = max(0, min(100, s)); c.details = "; ".join(d) or "创新性不足"; c.suggestions = ["尝试独特视角"]

    def _grade(self, s: float) -> str:
        if s >= 90: return "S - 传世经典"
        if s >= 80: return "A - 优秀佳作"
        if s >= 70: return "B - 品质良好"
        if s >= 60: return "C - 及格水准"
        if s >= 40: return "D - 需要打磨"
        return "F - 需要重写"

    def _summary(self, r: EvalResult) -> str:
        strong = [c.name for c in r.criteria.values() if c.score >= 70]
        weak = [c.name for c in r.criteria.values() if c.score < 50]
        s = f"综合评价：{r.grade}（{r.overall_score:.1f}分）。"
        if strong: s += f"优势：{'、'.join(strong)}。"
        if weak: s += f"改进：{'、'.join(weak)}。"
        return s

    def get_full_standards(self) -> Dict:
        return {
            "grades": {"S": "传世经典 90+", "A": "优秀佳作 80+", "B": "品质良好 70+", "C": "及格 60+", "D": "需打磨 40+", "F": "需重写"},
            "dimensions": [{"name": v["name"], "weight": f"{int(v['weight']*100)}%", "desc": v["desc"]} for v in self.dims.values()],
            "target": "A（80分以上）",
            "auto_optimize": "未达标时自动分析薄弱维度，调整提示词和策略迭代直到达标"
        }
