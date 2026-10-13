@echo off
cd /d "%~dp0"
echo ======================================================================
echo   Running I-MACSI Research Evaluation Graph Suite
echo   Using project virtual environment: .venv\Scripts\python.exe
echo ======================================================================

.\.venv\Scripts\python.exe evaluation_graphs_new\generate_all_77_graphs.py
.\.venv\Scripts\python.exe organize_graphs_by_topic.py

echo.
echo All 77 graphs generated and organized into topic folders!
pause
