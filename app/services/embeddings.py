import os
import httpx


async def embed_texts(texts: list[str]) -> list[list[float]] | None:
    """OpenAI-compatible embeddings; None explicitly means lexical-only demo mode."""
    key = os.getenv("EMBEDDING_API_KEY") or os.getenv("LLM_API_KEY")
    if not key:
        return None
    base = os.getenv("EMBEDDING_BASE_URL") or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(base.rstrip("/") + "/embeddings",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": model, "input": texts})
        response.raise_for_status()
        values = sorted(response.json()["data"], key=lambda x: x["index"])
        if len(values) != len(texts):
            raise ValueError("Embedding provider returned an unexpected number of vectors")
        return [v["embedding"] for v in values]
