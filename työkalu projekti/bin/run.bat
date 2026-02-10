@echo off
cd /d "%~dp0"

:RESTART
REM Activate virtual environment if it exists
IF EXIST venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run the Python script
python bin\run.py

REM Ask user to press Enter to restart or any other key to quit
echo.
echo Press ENTER to restart the app, or any other key to exit.
set /p input="> "

if "%input%"=="" (
    goto RESTART
)

REM Exit batch file
exit
