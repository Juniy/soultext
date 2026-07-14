import os, json
from typing import Optional, Dict, Any, List, AsyncGenerator
from enum import Enum
from dataclasses import dataclass, field
import httpx


class LLMProvider(str, Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    CUSTOM = "custom"


@dataclass
class LLMConfig:
    provider: LLMProvider = LLMProvider.OPENAI
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o"
    max_tokens: int = 4096
    temperature: float = 0.8
    top_p: float = 0.95
    frequency_penalty: float = 0.3
    presence_penalty: float = 0.2
    timeout: int = 120


PROVIDER_DEFAULTS = {
    LLMProvider.OPENAI: {"base_url": "https://api.openai.com/v1", "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1-mini"]},
    LLMProvider.DEEPSEEK: {"base_url": "https://api.deepseek.com/v1", "models": ["deepseek-chat", "deepseek-reasoner"]},
    LLMProvider.ANTHROPIC: {"base_url": "https://api.anthropic.com/v1", "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229"]},
    LLMProvider.OLLAMA: {"base_url": "http://localhost:11434/v1", "models": ["llama3", "qwen2.5", "mistral"]},
}


class LLMClient:
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self._apply_env_overrides()
        self._http_client: Optional[httpx.AsyncClient] = None

    def _apply_env_overrides(self):
        env_key = os.environ.get("SOULTEXT_LLM_API_KEY", "")
        env_url = os.environ.get("SOULTEXT_LLM_BASE_URL", "")
        env_model = os.environ.get("SOULTEXT_LLM_MODEL", "")
        env_provider = os.environ.get("SOULTEXT_LLM_PROVIDER", "")
        if env_key: self.config.api_key = env_key
        if env_url: self.config.base_url = env_url
        if env_model: self.config.model = env_model
        if env_provider:
            try: self.config.provider = LLMProvider(env_provider)
            except ValueError: pass
        if not self.config.api_key:
            self.config.api_key = os.environ.get("OPENAI_API_KEY", "")
        if self.config.provider in PROVIDER_DEFAULTS and not self.config.base_url:
            self.config.base_url = PROVIDER_DEFAULTS[self.config.provider]["base_url"]

    @property
    def http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=httpx.Timeout(self.config.timeout))
        return self._http_client

    def update_config(self, **kwargs):
        for k, v in kwargs.items():
           if hasattr(self.config, k) and v is not None:
               if k == "provider" and isinstance(v, str):
                   try: setattr(self.config, k, LLMProvider(v))
                   except ValueError: pass
               else:
                   setattr(self.config, k, v)
        self._save_persisted()

    def _persisted_path(self) -> str:
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "llm_config.json")

    def _save_persisted(self):
        try:
            p = self._persisted_path()
            os.makedirs(os.path.dirname(p), exist_ok=True)
            data = {
                "provider": self.config.provider.value,
                "api_key": self.config.api_key,
                "base_url": self.config.base_url,
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            }
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to persist LLM config: {e}")

    def load_persisted(self):
        try:
            p = self._persisted_path()
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("api_key"):
                    self.config.api_key = data["api_key"]
                if data.get("base_url"):
                    self.config.base_url = data["base_url"]
                if data.get("model"):
                    self.config.model = data["model"]
                if data.get("provider"):
                    try: self.config.provider = LLMProvider(data["provider"])
                    except ValueError: pass
                if data.get("max_tokens"):
                    self.config.max_tokens = data["max_tokens"]
                if data.get("temperature"):
                    self.config.temperature = data["temperature"]
                return True
        except Exception as e:
            print(f"Failed to load persisted LLM config: {e}")
        return False

    async def test_connection(self) -> Dict:
        result = {"success": False, "message": "", "latency_ms": 0}
        if not self.config.api_key:
            result["message"] = "未配置 API Key"
            return result
        import time
        t0 = time.time()
        try:
            messages = [{"role": "user", "content": "你好，请回复'连接正常'这四个字，不要回复其他内容。"}]
            response = await self.chat(messages)
            latency = int((time.time() - t0) * 1000)
            if response and "error" not in response.lower():
                result["success"] = True
                result["message"] = f"响应: {response[:50]}... 延迟: {latency}ms"
                result["latency_ms"] = latency
            else:
                result["message"] = f"返回异常: {response[:100]}"
        except Exception as e:
            result["message"] = f"连接失败: {str(e)}"
        return result

    def _build_headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.config.provider == LLMProvider.ANTHROPIC:
            h["x-api-key"] = self.config.api_key
            h["anthropic-version"] = "2023-06-01"
        else:
            h["Authorization"] = f"Bearer {self.config.api_key}"
        return h

    def _build_body(self, messages: List[Dict], stream: bool = False) -> Dict:
        if self.config.provider == LLMProvider.ANTHROPIC:
            system = ""
            chat = []
            for m in messages:
                if m["role"] == "system":
                    system += m["content"] + "\n"
                else:
                    chat.append(m)
            return {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "system": system.strip(),
                "messages": chat,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "stream": stream,
            }
        return {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "frequency_penalty": self.config.frequency_penalty,
            "presence_penalty": self.config.presence_penalty,
            "stream": stream,
        }

    async def chat(self, messages: List[Dict], stream: bool = False) -> str:
        if not self.config.api_key:
            return self._mock_response(messages)
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"
        try:
            r = await self.http_client.post(url, headers=self._build_headers(), json=self._build_body(messages, stream), timeout=self.config.timeout)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Generation error: {str(e)}]"

    async def chat_stream(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        if not self.config.api_key:
            yield self._mock_response(messages)
            return
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"
        try:
            async with self.http_client.stream("POST", url, headers=self._build_headers(), json=self._build_body(messages, True), timeout=self.config.timeout) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if line.startswith("data: ") and not line.startswith("data: [DONE]"):
                        d = json.loads(line[6:])
                        delta = d.get("choices", [{}])[0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]
        except Exception as e:
            yield f"[Generation error: {str(e)}]"

    def _mock_response(self, messages: List[Dict]) -> str:
        last = messages[-1]["content"] if messages else ""
        if "??" in last or "outline" in last.lower():
            return self._mock_outline()
        elif "?" in last and ("?" in last or "chapter" in last.lower()):
            return self._mock_chapter()
        elif "??" in last or "revision" in last.lower():
            return self._mock_revision()
        else:
            return self._mock_polish()

    def _mock_outline(self) -> str:
        return ("# ????\n\n## ?????\n??????????????...\n\n## ????\n- ????????????????\n- ???????????\n- ????????????\n\n## ????\n1. ?????????\n2. ?????????\n3. ????????\n\n## ????\n?????????????")

    def _mock_chapter(self) -> str:
        return ("??? ????\n\n?????????????????????????????????????????\n\n\"????\"?????????????\n\n?????????????????????????\n\n\"????\"???????\n\n\"????????\"????????????????????????")

    def _mock_revision(self) -> str:
        return "???????\n\n???????????????????\n?????????????????????????????"

    def _mock_polish(self) -> str:
        return "???????\n\n????????????????????????\n???????????????????"

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    def get_provider_info(self) -> Dict:
        defaults = PROVIDER_DEFAULTS.get(self.config.provider, {})
        return {
           "provider": self.config.provider.value,
           "model": self.config.model,
           "base_url": self.config.base_url,
           "has_api_key": bool(self.config.api_key),
           "available_models": defaults.get("models", []),
        }
