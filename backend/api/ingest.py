from fastapi import APIRouter, Request, HTTPException, status
from ..models import IngestRequest, IngestResponse
from ..core.embedder import get_embedder
from ..core.vectorstore import get_vectorstore
from ..connectors.pdf import PDFConnector
from ..connectors.notion import NotionConnector
from ..connectors.confluence import ConfluenceConnector
from ..connectors.base import chunk_documents

router = APIRouter(prefix="/api", tags=["Ingest"])

@router.post("/ingest", response_model=IngestResponse)
async def ingest(req: IngestRequest, request: Request):
    tenant_id = request.state.tenant_id
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant not identified")
    
    embedder = get_embedder()
    vectorstore = get_vectorstore(tenant_id)
    
    docs = []
    
    if req.source_type == "pdf":
        connector = PDFConnector()
        paths = req.source_config.get("paths", [])
        if not paths:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing 'paths' for PDF source")
        docs = connector.fetch_multiple(paths)
    
    elif req.source_type == "notion":
        token = req.source_config.get("token")
        database_id = req.source_config.get("database_id")
        if not token or not database_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing 'token' or 'database_id' for Notion source")
        connector = NotionConnector(token)
        docs = connector.fetch_database(database_id)
    
    elif req.source_type == "confluence":
        base_url = req.source_config.get("base_url")
        username = req.source_config.get("username")
        api_token = req.source_config.get("api_token")
        space_key = req.source_config.get("space_key")
        if not all([base_url, username, api_token, space_key]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Confluence config fields")
        connector = ConfluenceConnector(base_url, username, api_token)
        docs = connector.fetch_space(space_key)
    
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown source type: {req.source_type}")
    
    if not docs:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No documents found to ingest")
    
    chunks, sources = chunk_documents(docs)
    embeddings = embedder.embed(chunks)
    vectorstore.add(embeddings, chunks, sources)
    
    return IngestResponse(
        status="ok",
        chunks_created=len(chunks),
        documents_processed=len(docs)
    )
