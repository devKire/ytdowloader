@echo off
echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Executando YouTube Downloader...
python -m src.main

pause