from fastapi import FastAPI
from app.routes.knowledge_base import router
from app.store import Store

def create_app() -> FastAPI:
    app = FastAPI(title="AI Knowledge Hub", version="0.1.0")
    app.state.store = Store()

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    app.include_router(router)
    return app

app = create_app()
