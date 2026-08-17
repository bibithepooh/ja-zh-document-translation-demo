@echo off
cd /d "%~dp0"
set "PYTHONIOENCODING=utf-8"
set "OFFERBOOK_MODEL_ROOT=D:\OfferBookLocalModels"
start "" http://127.0.0.1:4173/
".venv\Scripts\python.exe" server.py
pause

