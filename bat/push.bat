@echo off
FOR /F "tokens=*" %%g IN ('cd') do (SET PUSH_DIR%1=%%g)
echo|set /p="- Current path stored -"
