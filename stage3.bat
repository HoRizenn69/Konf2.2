@echo off
cd /d "%~dp0"
call cli.bat --package A --repo fixtures\repo_simple.txt --output out.svg --test-mode --print-graph
pause