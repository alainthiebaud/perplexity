
@echo off
setlocal
python "%~dp0main.py" || py "%~dp0main.py"
pause
