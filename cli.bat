@echo off
setlocal
cd /d "%~dp0"
set PYTHONPATH=.
where py >nul 2>&1 && goto runpy
where python >nul 2>&1 && goto runpython
echo ERROR: Python was not found.
echo Install Python 3 from python.org
pause
exit /b 1

:runpy
py -3 -m src.main %*
exit /b %errorlevel%

:runpython
python -m src.main %*
exit /b %errorlevel%