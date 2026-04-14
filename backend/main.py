from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

from .middleware.auth import TenantMiddleware, load_tenants
from .api import rag, ingest, tenants

def create_app() -> FastAPI:
    load_tenants()
    
    app = FastAPI(
        title="AegisAI RAG API",
        description="Multi-tenant document Q&A platform",
        version="1.0.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TenantMiddleware)
    
    app.include_router(rag.router)
    app.include_router(ingest.router)
    app.include_router(tenants.router)
    
    frontend_path = Path(__file__).parent.parent.parent / "frontend"
    if frontend_path.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    
    @app.get("/")
    async def root():
        frontend_index = frontend_path / "index.html"
        if frontend_index.exists():
            return RedirectResponse(url="/static/index.html")
        return {"message": "AegisAI RAG API", "docs": "/docs", "version": "1.0.0"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    return app

app = create_app()
