from fastapi import FastAPI
from app.routes.knowledge_base import router
from app.routes.documents import router as documents_router
from app.routes.chat import router as chat_router
from app.db import make_session_factory

def create_app(session_factory=None) -> FastAPI:
    app = FastAPI(title="AI Knowledge Hub", version="1.0.0")
    app.state.session_factory = session_factory or make_session_factory()

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    app.include_router(router)
    app.include_router(documents_router)
    app.include_router(chat_router)
    return app

app = create_app()
