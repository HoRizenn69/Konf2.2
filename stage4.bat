@echo off
cd /d "%~dp0"
call cli.bat --package A --repo fixtures\repo_simple.txt --output order.svg --test-mode --load-order
pause