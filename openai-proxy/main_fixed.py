"""
OpenAI-compatible proxy service for Jarvis (Fixed Version)
Forwarding requests to various AI models (OpenAI, Gemini, Zhipu, Kimi, etc.)
"""
from fastapi import FastAPI, HTTPException, Request
import httpx
import os
from typing import Dict, List

app = FastAPI(title="Jarvis OpenAI Proxy", version="1.0.0")

# Configuration
API_KEYS = os.getenv("PROXY_API_KEYS", "jarvis-local-secret").split(",")

# Model routing configuration
MODEL_ROUTES = {
    "glm-5": "zhipu",
    "glm-4.7": "zhipu",
    "kimi-k2.5": "nvidia",
}

async def forward_to_zhipu(messages: List[Dict], model: str, **kwargs):
    """Forward request to Zhipu GLM"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Zhipu API key not configured")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                **kwargs
            },
            timeout=60.0
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        return response.json()

async def forward_to_nvidia(messages: List[Dict], model: str, **kwargs):
    """Forward request to NVIDIA (Kimi)"""
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="NVIDIA API key not configured")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "moonshotai/kimi-k2.5",
                "messages": messages,
                **kwargs
            },
            timeout=60.0
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        return response.json()

def verify_api_key(request: Request) -> bool:
    """Verify Bearer token"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    
    token = auth_header.replace("Bearer ", "")
    return token in API_KEYS

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "jarvis-openai-proxy"}

@app.get("/v1/models")
async def list_models():
    """List available models"""
    return {
        "object": "list",
        "data": [
            {"id": "glm-4.7", "name": "Zhipu GLM-4.7"},
            {"id": "glm-5", "name": "Zhipu GLM-5"},
            {"id": "kimi-k2.5", "name": "Kimi K2.5"},
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """OpenAI Chat Completions compatible endpoint"""
    if not verify_api_key(request):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    model = body.get("model", "glm-4.7")
    messages = body.get("messages", [])
    
    if not messages:
        raise HTTPException(status_code=400, detail="Messages are required")
    
    # Build kwargs
    kwargs = {}
    if "temperature" in body:
        kwargs["temperature"] = body["temperature"]
    if "max_tokens" in body:
        kwargs["max_tokens"] = body["max_tokens"]
    if "top_p" in body:
        kwargs["top_p"] = body["top_p"]
    
    # Determine routing
    provider = MODEL_ROUTES.get(model, "zhipu")
    
    try:
        if provider == "zhipu":
            result = await forward_to_zhipu(messages, model, **kwargs)
        elif provider == "nvidia":
            result = await forward_to_nvidia(messages, model, **kwargs)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        return result
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Upstream failed: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
