import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path

from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from backend.graph_db.graph_store import NovelGraphStore

from backend.knowledge.knowledge_base import KnowledgeBase

from backend.evaluator.evaluator import NovelEvaluator
from backend.evaluator.optimizer import NovelOptimizer

from backend.generator.pipeline import GenerationPipeline

from backend.llm.client import LLMClient, LLMConfig

from backend.foreshadowing.tracker import ForeshadowingTracker

from backend.export.exporter import NovelExporter

from backend.api.routes import router, init



BD = Path(__file__).parent

DD = BD / "data"

DD.mkdir(exist_ok=True)



gs = NovelGraphStore(storage_path=str(DD / "novel_graph.json"))

kb = KnowledgeBase()

ev = NovelEvaluator()
opt = NovelOptimizer(ev)

llm = LLMClient()

gen = GenerationPipeline(kb, gs, ev, llm)

ft = ForeshadowingTracker()

ex = NovelExporter()





@asynccontextmanager

async def lifespan(app):

    gs.load()

    kb_stats = kb.get_statistics()

    gs_stats = gs.get_statistics()

    llm_info = llm.get_provider_info()

    print(f"Soultext started: {kb_stats['total']} techniques, {gs_stats['total_nodes']} nodes")

    print(f"LLM: {llm_info['provider']} / {llm_info['model']} (key: {'yes' if llm_info['has_api_key'] else 'no'})")

    print(f"Foreshadowing: {ft.get_statistics()['total_clues']} clues, Export: ready")

    yield

    gs.save()

    await llm.close()

    print("Soultext stopped")





app = FastAPI(title="Soultext", description="AI long-form novel creation engine", version="0.1.0", lifespan=lifespan)



app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)



init(gs, kb, gen, ev, llm, ft, ex, opt)

app.include_router(router)





@app.get("/")

async def root():

    return {"name": "Soultext", "version": "0.1.0", "status": "running"}

