 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import sys
from pathlib import Path
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import config
from app.api.routers import chat

# Define lifespan BEFORE app
@asynccontextmanager
async def lifespan(app):
    from app.core.llm_factory import _is_online
    mode = 'ONLINE — Groq 70B' if _is_online() else 'OFFLINE — Local 12B'
    logger.success(f'Lucky 38 online. LLM mode: {mode}')
    yield

# Now app can reference lifespan
app = FastAPI(title='Mr. House AI — Lucky 38', version='2.0.0', lifespan=lifespan)

app.add_middleware(CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://127.0.0.1:3000', '*'],
    allow_credentials=True, allow_methods=['*'], allow_headers=['*']
)

app.include_router(chat.router, prefix='/api', tags=['chat'])

@app.get('/')
async def root():
    return {'system': 'Lucky 38', 'status': 'ONLINE', 'version': '2.0.0'}

@app.get('/health')
async def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    print('=' * 60)
    print('  MR. HOUSE AI — LUCKY 38 v2.0')
    print(f'  Mode   : {config.get_mode()}')
    print(f'  Server : http://{config.API_HOST}:{config.API_PORT}')
    print('=' * 60)
    uvicorn.run('app.api.main:app',
                host=config.API_HOST,
                port=config.API_PORT,
                reload=False)