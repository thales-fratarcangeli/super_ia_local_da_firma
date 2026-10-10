@echo off
chcp 65001 >nul
title Instalar elias-v4 (modelo experimental)
cd /d "%~dp0"
setlocal

rem Baixa as partes do modelo (Release v4 no GitHub), junta e cria o modelo no Ollama.
rem Precisa: Ollama instalado, ~11 GB livres (5 GB do modelo + 5 GB do arquivo do Ollama) e internet.
set BASE=https://github.com/thales-fratarcangeli/super_ia_local_da_firma/releases/download/v4
set OLLAMA=%LOCALAPPDATA%\Programs\Ollama\ollama.exe

if exist elias_v4_q4km.gguf goto criar

echo Baixando as 3 partes do modelo (cerca de 5 GB no total)...
for %%P in (1 2 3) do (
    if not exist elias_v4_q4km.gguf.part%%P curl -L --fail -o elias_v4_q4km.gguf.part%%P %BASE%/elias_v4_q4km.gguf.part%%P || goto erro
)
echo Juntando as partes...
copy /b elias_v4_q4km.gguf.part1+elias_v4_q4km.gguf.part2+elias_v4_q4km.gguf.part3 elias_v4_q4km.gguf >nul || goto erro
del elias_v4_q4km.gguf.part1 elias_v4_q4km.gguf.part2 elias_v4_q4km.gguf.part3

:criar
echo Criando o modelo elias-v4 no Ollama...
"%OLLAMA%" create elias-v4 -f Modelfile.elias-v4 || goto erro
echo.
echo Pronto. Para usar no agente: set IA_MODELO=elias-v4 e abra o ia.bat
echo (o padrao do ia.bat continua sendo o qwen3:8b, que foi melhor na suite inedita)
pause
exit /b 0

:erro
echo.
echo Algo falhou. Confira a internet e o espaco em disco.
pause
exit /b 1
