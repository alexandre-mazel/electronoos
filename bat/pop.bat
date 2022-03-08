@echo off
FOR /F "tokens=*" %%g IN ('cd') do (SET POP_DIR=%%g)
echo|set /p="- Current path stored -"