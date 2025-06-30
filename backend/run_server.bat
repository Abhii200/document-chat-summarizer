@echo off
echo Starting DocuMind Backend...
echo.
echo Activating virtual environment...
call openr\Scripts\activate

echo.
echo Installing/updating dependencies...
pip install -q -r requirements.txt

echo.
echo Starting server...
echo.
python main.py

pause
