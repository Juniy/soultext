from typing import Dict, List, Optional, Any
from datetime import datetime

class GenerationPipeline:
    def __init__(self, knowledge_base=None, graph_store=None, evaluator=None, llm_client=None):
        self.kb = knowledge_base
        self.gs = graph_store
        self.ev = evaluator
        self.llm = llm_client
        self.history: List[Dict] = []

    def _setting(self, key: str, default: Any = None) -> Any:
        if self.llm and self.llm.config:
            return getattr(self.llm.config, key, default)
        return default

    async def generate_outline(self, idea: str, genre: str = "??", settings: Optional[Dict] = None) -> Dict:
        from backend.llm.prompts import build_outline_prompt
        enh = self.kb.get_prompt_enhancements("outline") if self.kb else []
        messages = build_outline_prompt(idea, genre, settings)

        content = ""
        if self.llm:
            content = await self.llm.chat(messages)
        else:
            content = self.llm._mock_response(messages) if self.llm else "????????"

        result = {
            "type": "outline",
            "idea": idea,
            "genre": genre,
            "content": content,
            "generated_at": datetime.now().isoformat(),
            "settings": settings or {},
            "techniques_applied": enh,
        }
        self.history.append(result)
        return result

    async def generate_chapter(self, novel_id: str, num: int, outline: Dict, settings: Optional[Dict] = None, ctx: Optional[Dict] = None) -> Dict:
        from backend.llm.prompts import build_chapter_prompt
        enh = self.kb.get_prompt_enhancements("chapter") if self.kb else []

        outline_summary = ""
        if isinstance(outline, dict):
            outline_summary = outline.get("content", str(outline))
        elif isinstance(outline, str):
            outline_summary = outline

        title = novel_id
        prev_chapters = []
        chars = ""
        scenes = ""
        world = ""

        if self.gs:
            try:
                chars_data = self.gs.get_character_network(novel_id)
                chars = str(chars_data) if chars_data else ""
            except:
                pass

        messages = build_chapter_prompt(
            novel_title=title,
            chapter_num=num,
            outline_summary=outline_summary,
            previous_chapters=prev_chapters,
            character_context=chars,
            scene_context=scenes,
            world_context=world,
            settings=settings,
        )

        content = ""
        if self.llm:
            content = await self.llm.chat(messages)
        else:
            content = self.llm._mock_response(messages) if self.llm else "????????"

        wc = len(content)
        chapter_data = {
            "type": "chapter",
            "novel_id": novel_id,
            "chapter_number": num,
            "title": f"?{num}?",
            "content": content,
            "word_count": wc,
            "generated_at": datetime.now().isoformat(),
            "status": "generated",
            "techniques_applied": enh,
        }
        self.history.append(chapter_data)
        return chapter_data

    async def revise_chapter(self, content: str, feedback: str, settings: Optional[Dict] = None) -> Dict:
        from backend.llm.prompts import build_revision_prompt
        enh = self.kb.get_prompt_enhancements("revision") if self.kb else []
        messages = build_revision_prompt(content, feedback, settings)

        revised = ""
        if self.llm:
            revised = await self.llm.chat(messages)
        else:
            revised = self.llm._mock_response(messages) if self.llm else "??????"

        result = {
            "type": "revision",
            "original": content,
            "feedback": feedback,
            "revised_content": revised,
            "generated_at": datetime.now().isoformat(),
            "techniques_applied": enh,
        }
        self.history.append(result)
        return result

    async def polish_text(self, content: str, settings: Optional[Dict] = None) -> Dict:
        from backend.llm.prompts import build_polish_prompt
        messages = build_polish_prompt(content, settings)

        polished = ""
        if self.llm:
            polished = await self.llm.chat(messages)
        else:
            polished = self.llm._mock_response(messages) if self.llm else "??????"

        result = {
            "type": "polish",
            "original": content,
            "polished_content": polished,
            "generated_at": datetime.now().isoformat(),
        }
        self.history.append(result)
        return result

    def get_pipeline_status(self) -> Dict:
        return {
            "total": len(self.history),
            "last": self.history[-1] if self.history else None,
            "stages": ["outline", "chapter", "revision", "polish"],
            "llm_configured": self.llm is not None and bool(self.llm.config.api_key),
            "llm_provider": self.llm.get_provider_info() if self.llm else None,
        }
