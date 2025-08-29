@echo off
echo ========================================
echo    News Engine 停止脚本
echo ========================================
echo

echo 正在停止所有服务...

REM 停止API服务
taskkill /f /im python.exe /fi "WINDOWTITLE eq API Service*" >nul 2>&1
echo API服务已停止

REM 停止Celery Worker
taskkill /f /im python.exe /fi "WINDOWTITLE eq Celery Worker*" >nul 2>&1
echo Celery Worker已停止

REM 停止Celery Beat
taskkill /f /im python.exe /fi "WINDOWTITLE eq Celery Beat*" >nul 2>&1
echo Celery Beat已停止

REM 停止Redis服务
taskkill /f /im redis-server.exe >nul 2>&1
echo Redis服务已停止

echo.
echo ========================================
echo    所有服务已停止！
echo ========================================
echo.
pause
