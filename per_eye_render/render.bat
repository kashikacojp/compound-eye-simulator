REM set PYTHON_EXE=%~dp0..\Python311\python.exe
set PYTHON_EXE=python
%PYTHON_EXE% %~dp0..\per_eye_render\render.py %*
pause
