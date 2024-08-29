set PYTHON_EXE=%~dp0..\..\Python311\python.exe
%PYTHON_EXE% %~dp0..\step2-equirectangular-clipping\code\ui_viewer.py --setting %~dp0..\step2-equirectangular-clipping\settings\settings.toml
pause
