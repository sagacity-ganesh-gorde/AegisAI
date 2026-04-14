import httpx
import os
from typing import Optional

class LLMClient:
    def __init__(self, base_url: str = None, model: str = None, cpu_model: str = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
        self.cpu_model = cpu_model or os.getenv("OLLAMA_MODEL_CPU", "phi3:3.8b")
        self.gpu_available = self._check_gpu()
    
    def _check_gpu(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except:
            return False
    
    @property
    def active_model(self) -> str:
        return self.cpu_model if not self.gpu_available else self.model
    
    async def generate(self, prompt: str, system: str = None, context: str = None, temperature: float = 0.3) -> str:
        full_prompt = prompt
        if system:
            full_prompt = f"System: {system}\n\n{full_prompt}"
        if context:
            full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}\n\nAnswer:"
        
        payload = {
            "model": self.active_model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": 4096,
            }
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            return resp.json()["response"]
    
    async def chat(self, messages: list[dict]) -> str:
        payload = {
            "model": self.active_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_ctx": 4096,
            }
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            return resp.json()["message"]["content"]


_llm: Optional[LLMClient] = None

def get_llm() -> LLMClient:
    global _llm
    if _llm is None:
        _llm = LLMClient()
    return _llm
