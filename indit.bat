@echo off
title Dreamy Widget Indito
echo 🌙 Dreamy Widget inditasa folyamatban...
cd /d "%~dp0"
streamlit run gui\dreamy_web.py --server.enableStaticServing True
pause