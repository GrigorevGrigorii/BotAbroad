@echo off

SETLOCAL EnableDelayedExpansion
@CHCP 65001 >NUL

:: создание виртуального окружения
echo Создание виртуального окружения...
python3 -m venv venv
echo Виртуальное окружение создано
echo.

:: устанавка зависимостей в виртуальном окружении
echo Устанавка зависимостей в виртуальном окружении...
echo.
cmd /k "venv\Scripts\activate & pip3 install -r requirements.txt & deactivate"
echo.
echo Зависимости в виртуальном окружении установлены
echo.