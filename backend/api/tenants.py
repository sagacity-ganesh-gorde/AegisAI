from fastapi import APIRouter, Request, HTTPException, status
from ..models import TenantResponse
from ..core.vectorstore import get_vectorstore
from ..middleware.auth import get_tenant, tenant_keys
import os

router = APIRouter(prefix="/api", tags=["Tenants"])

@router.get("/me", response_model=TenantResponse)
async def get_current_tenant(request: Request):
    tenant_id = request.state.tenant_id
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant not identified")
    
    vectorstore = get_vectorstore(tenant_id)
    
    return TenantResponse(
        name=tenant_id,
        document_count=vectorstore.count(),
        index_status="ready" if vectorstore.count() > 0 else "empty"
    )

@router.get("/tenants")
async def list_tenants():
    return {"tenants": [{"name": name} for name in tenant_keys.values()]}
