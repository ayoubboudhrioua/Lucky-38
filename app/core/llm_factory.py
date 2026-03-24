import os, socket 
from loguru import logger 
from app.config import config 
  
def _is_online() -> bool: 
    """Check real connectivity — not just the network adapter.""" 
    try: 
        socket.setdefaulttimeout(3) 
        socket.create_connection(('api.groq.com', 443)) 
        return True 
    except OSError: 
        return False 
  
def get_llm(mode: str = 'smart'): 
    """ 
    Returns best available LLM. Never raises — always falls back. 
    mode='smart' : 70B for reasoning, planning, tool analysis 
    mode='fast'  : 8B for sensor queries, simple status checks 
    """ 
    online = _is_online() 
    providers = _online_providers(mode) if online else [] 
    providers += _local_providers(mode)  # always append local fallback 
  
    for name, build_fn in providers: 
        try: 
            llm = build_fn() 
            logger.info(f'LLM active: {name} ({mode} mode)') 
            return llm 
        except Exception as e: 
            logger.warning(f'{name} unavailable: {e}') 
            continue 
  
    raise RuntimeError('All LLM providers failed — check Ollama is running') 
  
def _online_providers(mode: str) -> list: 
    smart = (mode == 'smart') 
    providers = [] 
  
    if config.GROQ_API_KEY: 
        from langchain_groq import ChatGroq 
        providers.append(( 
            f'Groq-{"70B" if smart else "8B"}', 
            lambda: ChatGroq( 
                model=config.GROQ_SMART_MODEL if smart else 
config.GROQ_FAST_MODEL, 
                temperature=0.25, 
                max_tokens=2048, 
                groq_api_key=config.GROQ_API_KEY 
            ) 
        )) 
  
    if config.GOOGLE_API_KEY: 
        from langchain_google_genai import ChatGoogleGenerativeAI 
        providers.append(( 
            'Gemini-2.0-Flash', 
            lambda: ChatGoogleGenerativeAI( 
                model=config.GEMINI_MODEL, 
                temperature=0.25, 
                google_api_key=config.GOOGLE_API_KEY 
            ) 
        )) 
  
    return providers 
  
def _local_providers(mode: str) -> list: 
    smart = (mode == 'smart') 
    from langchain_ollama import OllamaLLM 
    return [( 
        f'Local-Ollama-{"12B" if smart else "8B"}', 
        lambda: OllamaLLM( 
            model=config.LOCAL_SMART_MODEL if smart else 
config.LOCAL_FAST_MODEL, 
            temperature=0.25, 
            num_gpu=1, 
            num_ctx=32768, 
            base_url=config.OLLAMA_BASE_URL 
        ) 
    )] 
