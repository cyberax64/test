import httpx
import json
import asyncio
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from database import Database

app = FastAPI(title="Ollama API Gateway")
db = Database()

# --- CONFIGURATION ---
OLLAMA_URL = "http://127.0.0.1:11434"
# ---------------------

# Client global pour réutiliser les connexions
client = httpx.AsyncClient(base_url=OLLAMA_URL, timeout=None)

async def get_user(request: Request):
    """
    Vérifie la clé API dans la DB et retourne les infos utilisateur.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    
    key = auth_header.split(" ")[1]
    user = db.get_user_by_api_key(key)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or inactive API Key",
        )
    
    if user['tokens_used'] >= user['token_quota']:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Token quota exceeded",
        )
        
    return user

async def process_and_log_tokens(response_iter, api_key, endpoint, model):
    """
    Générateur qui accumule la réponse pour extraire les tokens à la fin.
    """
    full_body = b""
    
    async for chunk in response_iter:
        full_body += chunk
        yield chunk
    
    # Une fois que tout est reçu, on analyse le contenu complet
    try:
        decoded_content = full_body.decode('utf-8', errors='ignore').strip()
        if not decoded_content:
            return

        prompt_tokens = 0
        completion_tokens = 0

        # Tentative 1 : Format JSON unique (OpenAI ou Ollama non-stream)
        try:
            data = json.loads(decoded_content)
            if "usage" in data:  # Format OpenAI
                prompt_tokens = data["usage"].get("prompt_tokens", 0)
                completion_tokens = data["usage"].get("completion_tokens", 0)
            else:  # Format Ollama natif
                prompt_tokens = data.get('prompt_eval_count', 0)
                completion_tokens = data.get('eval_count', 0)
        
        except json.JSONDecodeError:
            # Tentative 2 : Format Multi-JSON (Ollama native stream ou SSE)
            # On cherche les stats dans la toute dernière ligne JSON valide
            lines = decoded_content.split('\n')
            for line in reversed(lines):
                line = line.strip()
                if not line: continue
                if line.startswith("data: "): line = line[6:] # Nettoyage SSE
                if line == "[DONE]": continue
                
                try:
                    data = json.loads(line)
                    # On cherche les stats dans cet objet
                    p = data.get('prompt_eval_count') or data.get('usage', {}).get('prompt_tokens', 0)
                    c = data.get('eval_count') or data.get('usage', {}).get('completion_tokens', 0)
                    if p or c:
                        prompt_tokens, completion_tokens = p, c
                        break
                except:
                    continue

        total_tokens = prompt_tokens + completion_tokens
        
        if total_tokens > 0:
            print(f"✅ LOG: {total_tokens} tokens (In: {prompt_tokens} / Out: {completion_tokens}) pour {api_key[:12]}...")
            db.consume_tokens(api_key, total_tokens, endpoint, model, "success")
        else:
            print(f"⚠️ LOG: Aucun token détecté pour {model} (Endpoint: {endpoint})")
            
    except Exception as e:
        print(f"❌ ERREUR lors de l'analyse finale: {e}")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_ollama(path: str, request: Request, user: dict = Depends(get_user)):
    """
    Relaye les requêtes et décompte les tokens.
    """
    url = f"/{path}"
    
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("authorization", None)
    headers.pop("content-length", None)

    content = await request.body()
    params = request.query_params
    
    model_name = "unknown"
    if content:
        try:
            body_json = json.loads(content)
            model_name = body_json.get("model", "unknown")
        except:
            pass

    req = client.build_request(
        method=request.method,
        url=url,
        headers=headers,
        content=content,
        params=params,
    )

    try:
        response = await client.send(req, stream=True)
    except Exception as e:
        print(f"Erreur de connexion à Ollama: {e}")
        raise HTTPException(status_code=502, detail="Ollama injoignable")

    if response.status_code == 200 and request.method == "POST":
        return StreamingResponse(
            process_and_log_tokens(response.aiter_raw(), user['api_key'], path, model_name),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    else:
        return StreamingResponse(
            response.aiter_raw(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )

if __name__ == "__main__":
    import uvicorn
    print("🚀 API Gateway Ollama ready sur http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)