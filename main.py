# main.py
import os
import logging
from contextlib import asynccontextmanager
from typing import List
import time
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from embedding_service import ColpaliEmbeddingService

# --- setup ---
load_dotenv() 

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY no encontrada en las variables de entorno. Crea un archivo .env")

API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    """Valida el header 'Authorization: Bearer <token>'"""
    if api_key and api_key.startswith("Bearer ") and api_key.split(" ")[1] == API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Credenciales inválidas o ausentes")

class EmbeddingRequest(BaseModel):
    input_type: str = Field(..., description="Tipo de input, debe ser 'text' o 'image'.", pattern="^(text|image)$")
    inputs: List[str] = Field(..., description="Lista de strings (textos o imágenes en base64).")
    
class EmbeddingResponse(BaseModel):
    embeddings: List[List[List[float]]]

lifespan_context = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carga el modelo al iniciar la API y lo mantiene en memoria."""
    print("--- Cargando el modelo Colpali... (puede tardar varios minutos la primera vez) ---")
    lifespan_context["embedding_service"] = ColpaliEmbeddingService()
    print("--- Modelo cargado exitosamente. La API está lista. ---")
    yield
    lifespan_context.clear()
    print("--- API apagada. ---")

app = FastAPI(
    title="Colpali Embedding Service",
    description="API para generar embeddings multi-vectoriales usando Colpali.",
    lifespan=lifespan
)
logger = logging.getLogger("uvicorn")

@app.get("/gpu-check", summary="Verificar estado del servicio")
def health_check():
    """Endpoint simple para saber si la API está funcionando."""
    return {"status": "ok", "model_loaded": "embedding_service" in lifespan_context}

@app.post(
    "/embeddings",
    response_model=EmbeddingResponse,
    dependencies=[Depends(get_api_key)],
    summary="Generar Embeddings"
)

async def create_embeddings(request: EmbeddingRequest):
    """
    Recibe una lista de textos o imágenes y devuelve sus embeddings multi-vectoriales.
    """
    service: ColpaliEmbeddingService = lifespan_context["embedding_service"]
    
    try:
        logger.info(f"Recibida petición para {len(request.inputs)} inputs de tipo '{request.input_type}'.")
        start_time = time.time()
        
        if request.input_type == "text":
            embeddings_np = service.embed_texts(request.inputs)
        else: # es "image"
            embeddings_np = service.embed_images(request.inputs)
        
        # El modelo devuelve una lista de arrays numpy (cada uno es un multi-vector).
        # Convertimos cada array a una lista de Python para la respuesta JSON.
        embeddings_list = [arr.tolist() for arr in embeddings_np]
        
        total_time = time.time() - start_time
        logger.info(f"Petición completada en {total_time:.2f} segundos.")
        
        return EmbeddingResponse(embeddings=embeddings_list)

    except Exception as e:
        logger.error(f"Error procesando la petición: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")
    
    

