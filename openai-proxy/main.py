"""
OpenAI-compatible proxy service for Jarvis
Forwarding requests to various AI models (OpenAI, Gemini, Zhipu, Kimi, etc.)
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
import os
from typing import Dict, Any, List
import json

app = FastAPI(title="Jarvis OpenAI Proxy", version="1.0.0")

# Configuration
API_KEYS = os.getenv("PROXY_API_KEYS", "jarvis-local-secret").split(",")
SERVER_PORT = int(os.getenv("PORT", "9000"))

# Model routing configuration
MODEL_ROUTES = {
    # OpenAI models
    "gpt-4.1-mini": "openai",
    "gpt-4.1": "openai",
    "gpt-4o": "openai",
    "gpt-4o-mini": "openai",
    "gpt-3.5-turbo": "openai",
    
    # Gemini models
    "gemini-3-flash": "gemini",
    "gemini-3-pro": "gemini",
    "gemini-2-flash": "gemini",
    
    # Zhipu models
    "glm-5": "zhipu",
    "glm-4.7": "zhipu",
    
    # Kimi models
    "kimi-k2.5": "nvidia",
    
    # Default
    "jarvis-default": "zhipu",
}

async def forward_to_openai(messages: List[Dict], model: str, **kwargs):
    """Forward request to OpenAI"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
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
        return response.json()

async def forward_to_zhipu(messages: List[Dict], model: str, **kwargs):
    """Forward request to Zhipu GLM"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Zhipu API key not configured")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions",
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
            error_text = response.text
            try:
                error_json = response.json()
                error_detail = error_json.get("error", error_text)
            except:
                error_detail = error_text
            raise HTTPException(status_code=response.status_code, detail=error_detail)
        
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
            error_text = response.text
            try:
                error_json = response.json()
                error_detail = error_json.get("error", error_text)
            except:
                error_detail = error_text
            raise HTTPException(status_code=response.status_code, detail=error_detail)
        
        return response.json()

async def forward_to_gemini(messages: List[Dict], model: str, **kwargs):
    """Forward request to Gemini (using OpenAI-compatible endpoint)"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    # Convert OpenAI format to Gemini format
    contents = []
    for msg in messages:
        role = msg["role"]
        if role == "system":
            role = "user"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
            headers={"Content-Type": "application/json"},
            json={"contents": contents},
            timeout=60.0
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        data = response.json()
        
        # Convert Gemini response to OpenAI format
        candidates = data.get("candidates", [])
        if not candidates:
            raise HTTPException(status_code=500, detail="No response from Gemini")
        
        content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        
        return {
            "id": f"chatcmpl-{os.urandom(12).hex()}",
            "object": "chat.completion",
            "created": int(os.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }]
        }

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

@app.get("/models")
async def list_models():
    """List available models"""
    return {
        "object": "list",
        "data": [
            {"id": "glm-4.7", "name": "Zhipu GLM-4.7", "provider": "zhipu"},
            {"id": "glm-5", "name": "Zhipu GLM-5", "provider": "zhipu"},
            {"id": "kimi-k2.5", "name": "Kimi K2.5", "provider": "nvidia"},
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """OpenAI Chat Completions compatible endpoint"""
    # Verify API key
    if not verify_api_key(request):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Parse request
    body = await request.json()
    model = body.get("model", "glm-4.7")  # Default to Zhipu
    messages = body.get("messages", [])
    
    # Extract optional parameters
    temperature = body.get("temperature")
    max_tokens = body.get("max_tokens")
    top_p = body.get("top_p")
    
    # Build kwargs for optional parameters
    kwargs = {}
    if temperature is not None:
        kwargs["temperature"] = temperature
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if top_p is not None:
        kwargs["top_p"] = top_p
    
    # Determine routing
    provider = MODEL_ROUTES.get(model, "zhipu")  # Default to Zhipu
    
    try:
        # Forward to appropriate provider
        if provider == "openai":
            result = await forward_to_openai(
                messages=messages,
                model=model,
                **kwargs
            )
        elif provider == "zhipu":
            result = await forward_to_zhipu(
                messages=messages,
                model=model,
                **kwargs
            )
        elif provider == "nvidia":
            result = await forward_to_nvidia(
                messages=messages,
                model=model,
                **kwargs
            )
        elif provider == "gemini":
            result = await forward_to_gemini(
                messages=messages,
                model=model,
                **kwargs
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        return result
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Upstream request failed: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting Jarvis OpenAI Proxy on port {SERVER_PORT}")
    print(f"📝 Accepted API keys: {API_KEYS}")
    print(f"🤖 Available models: Zhipu (glm-4.7, glm-5), Kimi (kimi-k2.5)")
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
