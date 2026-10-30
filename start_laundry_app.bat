@echo off
title Smart Clean Laundry POS
echo ==============================================================
echo       SMART CLEAN LAUNDRY POS - KHMER / ENGLISH LOCAL SERVER
echo ==============================================================
echo.
echo Database: PostgreSQL (localhost:5432/laundry_db)
echo App URL:  http://localhost:8000/pos/
echo Admin:    http://localhost:8000/admin/
echo.
echo [INFO] Starting Django local server on http://0.0.0.0:8000 ...
echo [INFO] Press Ctrl+C to stop the server anytime.
echo.
venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
pause
