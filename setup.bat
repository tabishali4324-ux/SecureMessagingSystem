@echo off
echo ===================================
echo   Setting up SecureMessagingSystem
echo ===================================

echo.
echo [1/6] Checking virtual environment...
if exist venv (
    echo venv already exists, skipping creation.
) else (
    python -m venv venv
)

echo.
echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/6] Installing Django and cryptography...
pip install django
pip install cryptography

echo.
echo [4/6] Making migrations...
python manage.py makemigrations

echo.
echo [5/6] Applying migrations...
python manage.py migrate

echo.
echo [6/6] Creating default admin account...
python manage.py create_default_admin

echo.
echo ===================================
echo   Setup done! Starting server...
echo ===================================
python manage.py runserver

pause