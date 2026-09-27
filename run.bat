@echo off
title Panic Cloud

echo.
echo ===================================
echo            PANIC CLOUD
echo ===================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo First launch detected.
    echo Creating environment...
    echo.

    py -m venv .venv

    echo.
    echo Installing dependencies...
    echo.

    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)

echo.
echo Waking up the cloud...
echo.

".venv\Scripts\python.exe" main.py

echo.
echo RunAway has stopped.
echo.

pause