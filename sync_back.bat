@echo off 
SET "DEST=%~dp0" 
SET "DEST=%DEST:~0,-1%" 
SET "SOURCE=%1\lucky38\chroma_db" 
IF "%1"=="" ( 
echo Usage: sync_back.bat DRIVE_LETTER: 
pause & exit 
) 
echo [*] Pulling knowledge base from flash drive... 
robocopy "%SOURCE%" "%DEST%\chroma_db" /MIR 
echo [OK] Knowledge base synchronized. 
pause