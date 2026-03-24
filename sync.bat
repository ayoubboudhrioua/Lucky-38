@echo off 
:: Update flash drive with latest code 
:: Usage: sync.bat E:  (where E: is your flash drive letter) 
  
SET "SOURCE=%~dp0" 
SET "SOURCE=%SOURCE:~0,-1%" 
SET "DEST=%1\lucky38" 
  
IF "%1"=="" ( 
    echo Usage: sync.bat DRIVE_LETTER: 
    echo Example: sync.bat E: 
    pause & exit 
) 
  
echo [*] Syncing code to %DEST%... 
robocopy "%SOURCE%\app"      "%DEST%\app"      /MIR /XD .venv __pycache__ .git 
robocopy "%SOURCE%\chroma_db" "%DEST%\chroma_db" /MIR 
copy "%SOURCE%\requirements.txt" "%DEST%\requirements.txt" 
copy "%SOURCE%\start.bat"         "%DEST%\start.bat" 
copy "%SOURCE%\.env"              "%DEST%\.env" 
echo [OK] Sync complete. .venv excluded — will rebuild on first run. 
pause 