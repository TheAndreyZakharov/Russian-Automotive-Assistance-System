@echo off
chcp 65001 >nul

echo [RAAS Launcher] Запуск основных модулей...

:: 1. world_setup: spawn_vehicle.py
start cmd /k "cd /d C:\Proj\raas_project\world_setup && python spawn_vehicle.py"

timeout /t 5 /nobreak >nul

:: 2. main_func: third_person_camera.py
start cmd /k "cd /d C:\Proj\raas_project\main_func && python third_person_camera.py"

timeout /t 5 /nobreak >nul

:: 3. main_func: custom_control.py
start cmd /k "cd /d C:\Proj\raas_project\main_func && python custom_control.py"

timeout /t 5 /nobreak >nul

:: 4. raas_func: multimedia_panel.py
start cmd /k "cd /d C:\Proj\raas_project\raas_func && python multimedia_panel.py"

echo Все модули RAAS запущены.
