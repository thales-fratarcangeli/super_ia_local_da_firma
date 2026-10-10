@echo off
chcp 65001 >nul
title IA local - elias_ia_firma
cd /d "%~dp0"

rem Garante que o Ollama esta rodando
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo Iniciando o Ollama...
    set OLLAMA_FLASH_ATTENTION=1
    set OLLAMA_KEEP_ALIVE=60m
    start "" /min "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
    timeout /t 6 /nobreak >nul
)

rem Modelo de busca do RAG (baixa so na primeira vez)
"%LOCALAPPDATA%\Programs\Ollama\ollama.exe" list | findstr /i "nomic-embed-text" >nul || "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" pull nomic-embed-text

rem Modelo padrao: troque aqui (ex.: set IA_MODELO=elias-v2) quando houver um modelo melhor
if "%IA_MODELO%"=="" set IA_MODELO=qwen3:8b

python ia.py --pasta "%~dp0workspace" --modelo %IA_MODELO%
echo.
pause
