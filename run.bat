@echo off
cd /d "%~dp0"
set PYTHONPATH=.
where py >nul 2>&1 && goto runpy
where python >nul 2>&1 && goto runpython
echo ERROR: Python was not found.
echo Install Python 3 from python.org
echo and tick Add python.exe to PATH.
pause
exit /b 1

:runpy
py -3 demo.py %*
exit /b %errorlevel%

:runpython
python demo.py %*
exit /b %errorlevel%
