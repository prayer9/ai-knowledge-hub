from fastapi import FastAPI
from app.routes.knowledge_base import router
from app.db import make_session_factory

def create_app(session_factory=None) -> FastAPI:
    app = FastAPI(title="AI Knowledge Hub", version="0.2.0")
    app.state.session_factory = session_factory or make_session_factory()

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    app.include_router(router)
    return app

app = create_app()
