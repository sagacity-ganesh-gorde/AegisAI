from fastapi import APIRouter, Request, HTTPException, status
from ..models import AskRequest, AskResponse
from ..core.embedder import get_embedder
from ..core.vectorstore import get_vectorstore
from ..core.llm import get_llm

router = APIRouter(prefix="/api", tags=["RAG"])

SYSTEM_PROMPT = """You are a helpful assistant answering questions based on provided context. 
Answer only using the context provided. If the answer cannot be found in the context, say "I don't have enough information to answer that question based on the available documents."
Be concise and specific. Cite relevant information from the sources."""

@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest, request: Request):
    tenant_id = request.state.tenant_id
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant not identified")
    
    embedder = get_embedder()
    vectorstore = get_vectorstore(tenant_id)
    llm = get_llm()
    
    if vectorstore.count() == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents indexed for this tenant. Please ingest documents first."
        )
    
    q_emb = embedder.embed_single(req.question)
    _, _, results = vectorstore.search(q_emb, k=req.top_k)
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No relevant documents found. Try rephrasing your question."
        )
    
    context = "\n\n".join([f"[Source: {r['source']}]\n{r['text']}" for r in results])
    
    answer = await llm.generate(
        prompt=req.question,
        system=SYSTEM_PROMPT,
        context=context,
        temperature=req.temperature
    )
    
    return AskResponse(
        answer=answer,
        sources=[{"text": r["text"][:200], "source": r["source"], "score": r["score"]} for r in results],
        model=llm.active_model,
        gpu_used=llm.gpu_available
    )
