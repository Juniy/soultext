import os
from fastapi import APIRouter, HTTPException, Body, Query
from typing import Dict, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.foreshadowing.tracker import ForeshadowingTracker, ForeshadowClue, ClueStatus
from backend.evaluator.optimizer import NovelOptimizer, OptimizationRun
from backend.export.exporter import NovelExporter
from backend.evaluator.optimizer import NovelOptimizer
router = APIRouter(prefix="/api", tags=["soultext"])


class NovelCreate(BaseModel):
    title: str = "???"
    genre: str = "??"
    description: str = ""
    author: str = ""


class ChapterReq(BaseModel):
    novel_id: str
    chapter_number: int
    outline: Optional[Dict] = None
    settings: Optional[Dict] = None


class EvalReq(BaseModel):
    text: str
    context: Optional[Dict] = None


class LLMSettings(BaseModel):
    provider: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


_novels: Dict[str, Dict] = {}
_gs = None
_kb = None
_gen = None
_ev = None
_llm = None
_ft = None
_ex = None
_opt = None


def init(gs, kb, gen, ev, llm=None, ft=None, ex=None, opt=None):
    global _gs, _kb, _gen, _ev, _llm, _ft, _ex, _opt
    _gs = gs
    _kb = kb
    _gen = gen
    _ev = ev
    _llm = llm
    _ft = ft
    _ex = ex
    _opt = opt


@router.get("/novels")
async def list_novels():
    return list(_novels.values())


@router.post("/novels")
async def create_novel(n: NovelCreate):
    nid = f"novel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    _novels[nid] = {
        "id": nid,
        "title": n.title,
        "genre": n.genre,
        "description": n.description,
        "author": n.author,
        "status": "idea",
        "word_count_target": 5000000,
        "word_count_current": 0,
        "chapters": [],
        "characters": {},
        "locations": {},
        "scenes": {},
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    return _novels[nid]


@router.get("/novels/{nid}")
async def get_novel(nid: str):
    if nid not in _novels:
        raise HTTPException(404, "???")
    n = _novels[nid]
    if _gs:
        try:
            n["character_network"] = _gs.get_character_network(nid)
            n["timeline"] = _gs.get_timeline_events(nid)
            n["graph_stats"] = _gs.get_statistics()
        except:
            pass
    return n


@router.post("/novels/{nid}/generate/outline")
async def gen_outline(nid: str, settings: Optional[Dict] = Body(None)):
    if nid not in _novels:
        raise HTTPException(404, "???")
    n = _novels[nid]
    if _gen:
        o = await _gen.generate_outline(n.get("description", ""), n.get("genre", "??"), settings)
        n["outline"] = o
        n["status"] = "outlining"
        return o
    return {"message": "Generator unavailable"}


@router.post("/novels/{nid}/generate/chapter")
async def gen_chapter(nid: str, req: ChapterReq):
    if nid not in _novels:
        raise HTTPException(404, "???")
    if _gen:
        ch = await _gen.generate_chapter(nid, req.chapter_number, req.outline or _novels[nid].get("outline", {}), req.settings)
        _novels[nid]["chapters"].append(ch)
        _novels[nid]["word_count_current"] += ch.get("word_count", 0)
        _novels[nid]["updated_at"] = datetime.now().isoformat()
        return ch
    return {"message": "Generator unavailable"}


@router.post("/evaluate")
async def evaluate(req: EvalReq):
    if not _ev:
        return {"message": "Evaluator unavailable"}
    return _ev.evaluate(req.text, req.context).to_dict()


@router.get("/evaluate/standards")
async def standards():
    if not _ev:
        return {"message": "Evaluator unavailable"}
    return _ev.get_full_standards()


@router.get("/knowledge/categories")
async def knowledge_cats():
    if not _kb:
        return {"message": "Knowledge base unavailable"}
    return {cat: [{"id": t.id, "title": t.title, "summary": t.summary} for t in ts]
            for cat, ts in _kb.get_all_categories().items()}


@router.get("/knowledge/search")
async def search_kb(q: str = Query("")):
    if not _kb:
        return {"message": "KB unavailable"}
    return [{"id": t.id, "title": t.title, "category": t.category, "summary": t.summary,
             "key_points": t.key_points} for t in _kb.search(q)]


@router.get("/graph/query")
async def query_graph(novel_id: str = Query(""), node_type: Optional[str] = Query(None), node_id: Optional[str] = Query(None)):
    if not _gs:
        return {"message": "Graph unavailable"}
    if node_id:
        nd = _gs.get_node(node_id)
        if not nd:
            raise HTTPException(404, "?????")
        return {"node": nd, "connections": _gs.get_connections(node_id)}
    if novel_id:
        if node_type == "character":
            return _gs.get_character_network(novel_id)
        if node_type == "timeline":
            return {"events": _gs.get_timeline_events(novel_id)}
        if node_type == "scene":
            return {"scenes": _gs.get_scene_sequence(novel_id)}
    return _gs.get_statistics()


@router.get("/graph/consistency")
async def consistency(novel_id: str = Query("")):
    if not _gs:
        return {"message": "Graph unavailable"}
    issues = _gs.get_consistency_issues(novel_id)
    return {"issues": issues, "count": len(issues)}


@router.get("/system/status")
async def status():
    llm_info = _llm.get_provider_info() if _llm else {"provider": "none", "has_api_key": False}
    return {
        "graph_store": _gs is not None,
        "knowledge_base": _kb is not None,
        "generator": _gen is not None,
        "evaluator": _ev is not None,
        "llm": llm_info,
        "novels": len(_novels),
        "nodes": _gs.get_statistics()["total_nodes"] if _gs else 0,
        "edges": _gs.get_statistics()["total_edges"] if _gs else 0,
    }


@router.get("/llm/settings")
async def get_llm_settings():
    if not _llm:
        return {"message": "LLM not configured"}
    return _llm.get_provider_info()


@router.post("/llm/settings")
async def update_llm_settings(s: LLMSettings):
    if not _llm:
        return {"message": "LLM not configured"}
    kwargs = {k: v for k, v in s.model_dump(exclude_none=True).items()}
    _llm.update_config(**kwargs)
    return _llm.get_provider_info()



@router.post("/llm/test")
async def test_llm():
    if not _llm:
        return {"message": "LLM not configured"}
    result = await _llm.test_connection()
    return result


@router.get("/generator/status")
async def gen_status():
    if not _gen:
        return {"message": "Generator unavailable"}
    return _gen.get_pipeline_status()


@router.post("/novels/{nid}/generate/revise")
async def gen_revise(nid: str, feedback: str = Body(""), text: str = Body(""), settings: Optional[Dict] = Body(None)):
    if nid not in _novels:
        raise HTTPException(404, "???")
    if _gen:
        target_text = text or (_novels[nid].get("chapters") or [{}])[-1].get("content", "")
        if not target_text:
            return {"message": "No text to revise"}
        result = await _gen.revise_chapter(target_text, feedback, settings)
        return result
    return {"message": "Generator unavailable"}


@router.post("/novels/{nid}/generate/polish")
async def gen_polish(nid: str, text: str = Body(""), settings: Optional[Dict] = Body(None)):
    if nid not in _novels:
        raise HTTPException(404, "???")
    if _gen:
        target_text = text or (_novels[nid].get("chapters") or [{}])[-1].get("content", "")
        if not target_text:
            return {"message": "No text to polish"}
        result = await _gen.polish_text(target_text, settings)
        return result
    return {"message": "Generator unavailable"}

# ====== Foreshadowing Routes ======

@router.post("/novels/{nid}/foreshadowing")
async def add_foreshadow_clue(nid: str, clue_data: Dict = Body(...)):
    if nid not in _novels:
        raise HTTPException(404, "?????")
    if not _ft:
        return {"message": "Foreshadowing tracker unavailable"}
    import uuid
    clue = ForeshadowClue(
        id=f"clue_{uuid.uuid4().hex[:8]}",
        novel_id=nid,
        description=clue_data.get("description", ""),
        clue_type=clue_data.get("clue_type", "general"),
        importance=clue_data.get("importance", 1),
        planted_chapter=clue_data.get("planted_chapter", 0),
        expected_recall_chapter=clue_data.get("expected_recall_chapter", 0),
        related_entities=clue_data.get("related_entities", []),
        keywords=clue_data.get("keywords", []),
        notes=clue_data.get("notes", ""),
    )
    _ft.add_clue(clue)
    return _ft._serialize_clue(clue)


@router.get("/novels/{nid}/foreshadowing")
async def list_foreshadow_clues(nid: str, status_filter: str = Query(None)):
    if not _ft:
        return {"message": "Foreshadowing tracker unavailable"}
    clues = _ft.get_novel_clues(nid)
    if status_filter:
        clues = [c for c in clues if c.status.value == status_filter]
    return {"clues": [_ft._serialize_clue(c) for c in clues], "total": len(clues)}


@router.get("/novels/{nid}/foreshadowing/active")
async def get_active_clues(nid: str):
    if not _ft:
        return {"message": "Foreshadowing tracker unavailable"}
    clues = _ft.get_active_clues(nid)
    return {"clues": [_ft._serialize_clue(c) for c in clues], "count": len(clues)}


@router.get("/novels/{nid}/foreshadowing/overdue")
async def get_overdue_clues(nid: str, current_chapter: int = Query(1)):
    if not _ft:
        return {"message": "Foreshadowing tracker unavailable"}
    clues = _ft.get_overdue_clues(nid, current_chapter)
    return {"clues": [_ft._serialize_clue(c) for c in clues], "count": len(clues)}


@router.put("/novels/{nid}/foreshadowing/{clue_id}/fulfill")
async def fulfill_foreshadow_clue(nid: str, clue_id: str, chapter: int = Body(0)):
    if not _ft:
        return {"message": "Foreshadowing tracker unavailable"}
    clue = _ft.fulfill_clue(clue_id, chapter)
    if not clue:
        raise HTTPException(404, "?????")
    return _ft._serialize_clue(clue)


@router.put("/novels/{nid}/foreshadowing/{clue_id}")
async def update_foreshadow_clue(nid: str, clue_id: str, update_data: Dict = Body(...)):
    if not _ft:
        return {"message": "Foreshadowing tracker unavailable"}
    clue = _ft.update_clue(clue_id, **update_data)
    if not clue:
        raise HTTPException(404, "?????")
    return _ft._serialize_clue(clue)


@router.delete("/novels/{nid}/foreshadowing/{clue_id}")
async def delete_foreshadow_clue(nid: str, clue_id: str):
    if not _ft:
        return {"message": "Foreshadowing tracker unavailable"}
    if not _ft.delete_clue(clue_id):
        raise HTTPException(404, "?????")
    return {"message": "???", "clue_id": clue_id}


@router.get("/foreshadowing/statistics")
async def foreshadowing_statistics():
    if not _ft:
        return {"message": "Foreshadowing tracker unavailable"}
    return _ft.get_statistics()


# ====== Optimization Routes ======

@router.post("/novels/{nid}/optimize/analyze")
async def optimize_analyze(nid: str):
    if nid not in _novels:
        raise HTTPException(404, "?????")
    if not _opt or not _ev:
        return {"message": "Optimizer unavailable"}
    # Analyze the latest chapter
    chapters = _novels[nid].get("chapters", [])
    if not chapters:
        return {"message": "No chapters to analyze"}
    latest = chapters[-1]
    eval_result = _ev.evaluate(latest.get("content", ""), {"novel_id": nid}).to_dict()
    analysis = _opt.analyze_evaluation(eval_result)
    adjustments = _opt.generate_adjustments(analysis, _novels[nid].get("settings", {}))
    return {
        "evaluation": eval_result,
        "analysis": analysis,
        "adjustments": adjustments,
        "target_achieved": _opt.is_target_achieved(eval_result),
    }


@router.post("/novels/{nid}/optimize/apply")
async def optimize_apply(nid: str):
    if nid not in _novels:
        raise HTTPException(404, "?????")
    if not _opt or not _ev:
        return {"message": "Optimizer unavailable"}
    chapters = _novels[nid].get("chapters", [])
    if not chapters:
        return {"message": "No chapters to optimize"}
    latest = chapters[-1]
    eval_result = _ev.evaluate(latest.get("content", ""), {"novel_id": nid}).to_dict()
    analysis = _opt.analyze_evaluation(eval_result)
    adjustments = _opt.generate_adjustments(analysis, _novels[nid].get("settings", {}))
    # Record optimization run
    from datetime import datetime
    run = OptimizationRun(
        timestamp=datetime.now().isoformat(),
        eval_score=eval_result.get("overall_score", 0),
        eval_grade=eval_result.get("grade", "F"),
        weak_dimensions=[w["name"] for w in analysis.get("weak", [])],
        suggestion=adjustments.get("adjustment_summary", ""),
        parameter_adjustments={},
        prompt_adjustments=adjustments.get("prompt_adjustments", []),
    )
    _opt.record_run(nid, run)
    # Apply adjustments to novel settings
    if "settings" not in _novels[nid]:
        _novels[nid]["settings"] = {}
    for k, v in adjustments.get("settings", {}).items():
        _novels[nid]["settings"][k] = v
    _novels[nid]["updated_at"] = datetime.now().isoformat()
    return {
        "evaluation": eval_result,
        "analysis": analysis,
        "adjustments": adjustments,
        "optimization_applied": True,
    }


@router.get("/novels/{nid}/optimize/history")
async def optimize_history(nid: str):
    if not _opt:
        return {"message": "Optimizer unavailable"}
    return {
        "history": _opt.get_optimization_history(nid),
        "status": _opt.get_optimization_status(nid),
    }


@router.get("/optimize/targets")
async def optimize_targets():
    return {
        "target_grade": NovelOptimizer.TARGET_GRADE,
        "target_score": NovelOptimizer.TARGET_SCORE,
        "dimension_map": list(NovelOptimizer.DIMENSION_PARAM_MAP.keys()),
        "max_iterations": NovelOptimizer.max_iterations if hasattr(NovelOptimizer, "max_iterations") else 5,
    }


# ====== Export Routes ======

@router.post("/novels/{nid}/export")
async def export_novel(nid: str, fmt: str = Query("txt")):
    if nid not in _novels:
        raise HTTPException(404, "?????")
    if not _ex:
        return {"message": "Exporter unavailable"}
    try:
        filepath = _ex.export(_novels[nid], fmt)
        filename = os.path.basename(filepath)
        return {"message": "????", "filepath": filepath, "filename": filename, "format": fmt}
    except Exception as e:
        raise HTTPException(500, f"????: {str(e)}")


@router.get("/novels/{nid}/export/formats")
async def export_formats(nid: str):
    if nid not in _novels:
        raise HTTPException(404, "?????")
    return {"formats": ["txt", "epub"], "current_chapters": len(_novels[nid].get("chapters", [])),
            "word_count": _novels[nid].get("word_count_current", 0)}
