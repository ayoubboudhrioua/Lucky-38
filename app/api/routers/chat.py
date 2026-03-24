from fastapi import APIRouter, HTTPException 
from fastapi.responses import StreamingResponse 
from pydantic import BaseModel 
import json 
from loguru import logger 
  
from app.core import agent as house_agent 
from app.core.privacy_filter import sanitize 
  
router = APIRouter() 
  
class ChatRequest(BaseModel): 
    message: str 
  
class ChatResponse(BaseModel): 
    response: str 
    mode: str = 'unknown' 
  
@router.post('/chat', response_model=ChatResponse) 
async def chat(request: ChatRequest): 
    """ 
    Send message to Mr. House and get full response. 
    Replaces your original /chat endpoint. 
    The agent handles LLM routing, tool calls, and memory automatically. 
    """ 
    try: 
        # Sanitize input before it touches any external API 
        clean_message = sanitize(request.message) 
        response_text = house_agent.invoke(clean_message) 
        return ChatResponse(response=response_text, mode='agent') 
    except Exception as e: 
        logger.error(f'Agent error: {e}') 
        raise HTTPException(500, str(e)) 
  
@router.get('/status') 
async def status(): 
    """ 
    Check system status. 
    Replaces your original /test-ollama endpoint. 
    """ 
    from app.core.llm_factory import _is_online 
    from app.config import config 
    online = _is_online() 
    return { 
        'system': 'Lucky 38 Control System', 
        'status': 'ONLINE', 
        'connectivity': 'ONLINE' if online else 'OFFLINE', 
        'active_model': config.GROQ_SMART_MODEL if online else 
config.LOCAL_SMART_MODEL, 
        'mode': config.get_mode(), 
        'rag': 'active', 
        'memory': 'active' 
    } 
