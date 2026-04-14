from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import os

tenant_keys: dict[str, str] = {}

def load_tenants():
    global tenant_keys
    tenants_raw = os.getenv("TENANTS", "")
    if tenants_raw:
        for pair in tenants_raw.split(","):
            if "=" in pair:
                name, key = pair.split("=", 1)
                tenant_keys[key.strip()] = name.strip()

def get_tenant(key: str) -> Optional[str]:
    return tenant_keys.get(key)

api_key_header = APIKeyHeader(name="X-Tenant-Key", auto_error=False)

async def verify_tenant_key(key: str = api_key_header) -> str:
    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Tenant-Key header"
        )
    tenant = get_tenant(key)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return tenant

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        key = request.headers.get("X-Tenant-Key")
        tenant = get_tenant(key) if key else None
        
        if tenant:
            request.state.tenant_id = tenant
            request.state.tenant_key = key
        else:
            request.state.tenant_id = None
            request.state.tenant_key = None
        
        response = await call_next(request)
        return response
