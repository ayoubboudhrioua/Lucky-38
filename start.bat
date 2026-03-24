@echo off 
TITLE Lucky 38 — AI Overseer 
color 0C 
  
SET "BASE=%~dp0" 
SET "BASE=%BASE:~0,-1%" 
  
echo. 
echo   LUCKY 38 AI OVERSEER — INITIALIZING 
echo   ================================================ 
echo. 
  
:: ── Set portable paths if running from flash drive ── 
SET "CHROMA_DB_PATH=%BASE%\chroma_db" 
SET "KNOWLEDGE_PATH=%BASE%\app\knowledge\documents" 
  
:: ── Handle portable Ollama if present on drive ────── 
IF EXIST "%BASE%\ollama\ollama.exe" ( 
    SET "OLLAMA_MODELS=%BASE%\models" 
    SET "OLLAMA_HOME=%BASE%\ollama_data" 
    SET "OLLAMA_HOST=127.0.0.1:11434" 
    IF NOT EXIST "%BASE%\ollama_data" mkdir "%BASE%\ollama_data" 
    echo   [*] Portable Ollama detected — launching... 
    START "" /B "%BASE%\ollama\ollama.exe" serve 
    timeout /t 4 /nobreak ^>nul 
) ELSE ( 
    echo   [*] Using system Ollama installation 
) 
  
:: ── Load .env ──────────────────────────────────────── 
IF EXIST "%BASE%\.env" ( 
    FOR /F "usebackq tokens=1,2 delims==" %%A IN ("%BASE%\.env") DO SET %%A=%%B 
    echo   [OK] Environment loaded 
) ELSE ( 
    echo   [!!] .env missing — offline mode only 
) 
  
:: ── Check internet ─────────────────────────────────── 
ping -n 1 api.groq.com ^>nul 2^>^&1 
IF %ERRORLEVEL%==0 ( 
    echo   [OK] Network: ONLINE — Groq 70B active 
) ELSE ( 
    echo   [!!] Network: OFFLINE — local 12B fallback active 
) 
  
:: ── Build venv if missing ──────────────────────────── 
IF NOT EXIST "%BASE%\.venv" ( 
    echo   [*] First run — building environment (takes 2-3 minutes)... 
    python -m venv "%BASE%\.venv" 
    call "%BASE%\.venv\Scripts\activate" 
    pip install -r "%BASE%\requirements.txt" --quiet 
    echo   [OK] Environment ready 
) ELSE ( 
    call "%BASE%\.venv\Scripts\activate" 
) 
  
:: ── Launch ─────────────────────────────────────────── 
echo   [*] Starting Lucky 38 control system... 
echo   ================================================ 
echo. 
cd "%BASE%" 
python -m app.api.main 
  
:: ── Cleanup ────────────────────────────────────────── 
echo. 
echo   [*] Shutting down... 
IF EXIST "%BASE%\ollama\ollama.exe" taskkill /F /IM ollama.exe ^>nul 2^>^&1 
echo   The house always wins. 
pause