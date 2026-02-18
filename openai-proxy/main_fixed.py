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
    "gemini-2.0-flash": "gemini",
    "gemini-2.5-pro": "gemini",
    "gemini-2.5-flash": "gemini",
    "gemini-1.5-pro": "gemini",
    "gemini-1.5-flash": "gemini",
}

async def forward_to_zhipu(messages: List[Dict], model: str, **kwargs):
    """Forward request to Zhipu GLM"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Zhipu API key not configured")
    
    # Use the coding endpoint (same as OpenClaw config)
    url = "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
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

async def forward_to_gemini(messages: List[Dict], model: str, **kwargs):
    """Forward request to Google Gemini via OpenAI-compatible endpoint"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")

    # Map model names for Gemini OpenAI endpoint
    gemini_model_map = {
        "gemini-2.0-flash": "gemini-2.0-flash",
        "gemini-2.5-flash": "gemini-2.5-flash",
        "gemini-2.5-pro": "gemini-2.5-pro",
        "gemini-1.5-flash": "gemini-1.5-flash-001",
        "gemini-1.5-pro": "gemini-1.5-pro-001",
    }

    gemini_model = gemini_model_map.get(model, model)

    # Use OpenAI-compatible endpoint
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": gemini_model,
                "messages": messages,
                **kwargs
            },
            timeout=60.0
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        # Response is already in OpenAI format
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
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash"},
            {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"},
            {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
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
        elif provider == "gemini":
            result = await forward_to_gemini(messages, model, **kwargs)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        return result
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Upstream failed: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
