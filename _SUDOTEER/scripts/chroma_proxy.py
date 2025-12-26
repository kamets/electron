
import httpx
from fastapi import FastAPI, Request, Response
import uvicorn
import asyncio
import subprocess
import os
import sys
import time

app = FastAPI(title="ChromaDB Compatibility Proxy")

# Port 8000: The public port Vex/IDE connects to
# Port 8001: The internal port where modern Chroma v2 runs
CHROMA_INTERNAL_URL = "http://127.0.0.1:8001"

@app.get("/api/v1/heartbeat")
async def heartbeat():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{CHROMA_INTERNAL_URL}/api/v2/heartbeat", timeout=5.0)
            return Response(content=r.content, status_code=r.status_code, media_type=r.headers.get("content-type"))
    except Exception as e:
        return Response(content=f"Proxy error: {str(e)}", status_code=502)

@app.get("/api/v1/collections")
async def list_collections():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{CHROMA_INTERNAL_URL}/api/v2/tenants/default_tenant/databases/default_database/collections", timeout=5.0)
            return Response(content=r.content, status_code=r.status_code, media_type=r.headers.get("content-type"))
    except Exception as e:
        return Response(content=f"Proxy error: {str(e)}", status_code=502)

@app.post("/api/v1/collections")
async def create_collection(request: Request):
    try:
        content = await request.body()
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{CHROMA_INTERNAL_URL}/api/v2/tenants/default_tenant/databases/default_database/collections", content=content, timeout=5.0)
            return Response(content=r.content, status_code=r.status_code, media_type=r.headers.get("content-type"))
    except Exception as e:
        return Response(content=f"Proxy error: {str(e)}", status_code=502)

@app.api_route("/api/v1/collections/{collection_id}/{action}", methods=["GET", "POST", "PUT", "DELETE"])
async def collection_action(collection_id: str, action: str, request: Request):
    try:
        method = request.method
        content = await request.body()
        url = f"{CHROMA_INTERNAL_URL}/api/v2/tenants/default_tenant/databases/default_database/collections/{collection_id}/{action}"
        async with httpx.AsyncClient() as client:
            r = await client.request(method, url, content=content, timeout=10.0)
            return Response(content=r.content, status_code=r.status_code, media_type=r.headers.get("content-type"))
    except Exception as e:
        return Response(content=f"Proxy error: {str(e)}", status_code=502)

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(request: Request, path_name: str):
    # Fallback for other potential v1 calls
    # Simply try to forward to v1 first, if it fails, the user will know
    url = f"{CHROMA_INTERNAL_URL}/{path_name}"
    method = request.method
    content = await request.body()
    headers = dict(request.headers)

    # Remove host header to avoid conflicts
    if "host" in headers:
        del headers["host"]

    try:
        async with httpx.AsyncClient() as client:
            r = await client.request(method, url, content=content, headers=headers, timeout=10.0)
            return Response(content=r.content, status_code=r.status_code, media_type=r.headers.get("content-type"))
    except Exception as e:
        return Response(content=f"Proxy error: {str(e)}", status_code=502)

if __name__ == "__main__":
    print("Starting Chroma Compatibility Proxy on port 8000 -> 8001")
    uvicorn.run(app, host="0.0.0.0", port=8000)
