from fastapi import APIRouter, HTTPException, Body, Query
from typing import Dict, Optional
from pydantic import BaseModel
from datetime import datetime

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


def init(gs, kb, gen, ev, llm=None):
    global _gs, _kb, _gen, _ev, _llm
    _gs = gs
    _kb = kb
    _gen = gen
    _ev = ev
    _llm = llm


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
    kwargs = {k: v for k, v in s.dict(exclude_none=True).items()}
    _llm.update_config(**kwargs)
    return _llm.get_provider_info()


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
