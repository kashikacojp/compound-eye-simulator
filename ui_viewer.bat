REM set PYTHON_EXE=%~dp0..\..\Python311\python.exe
set PYTHON_EXE=python
%PYTHON_EXE% %~dp0\panorama_render\step2-equirectangular-clipping\code\ui_viewer.py --setting settings.toml
pause
