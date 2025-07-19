@echo off
chcp 65001 >nul
title Google Sheets 區塊瀏覽器資料自動處理工具

echo ==================================================
echo Google Sheets 區塊瀏覽器資料自動處理工具
echo ==================================================
echo.

:: 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：找不到 Python，請先安裝 Python 3.8 或更高版本
    echo 下載網址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 已安裝
python --version

:: 檢查必要檔案
if not exist "sheets_processor.py" (
    echo ❌ 錯誤：找不到 sheets_processor.py 檔案
    pause
    exit /b 1
)

if not exist "config.py" (
    echo ❌ 錯誤：找不到 config.py 檔案
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ❌ 錯誤：找不到 requirements.txt 檔案
    pause
    exit /b 1
)

echo ✅ 必要檔案檢查完成

:: 安裝依賴套件
echo.
echo 📦 安裝依賴套件...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 套件安裝失敗，請檢查網路連線
    pause
    exit /b 1
)

echo ✅ 套件安裝完成

:: 檢查憑證檔案
if not exist "credentials.json" (
    echo.
    echo ⚠️  警告：找不到 credentials.json 檔案
    echo 請先執行 python setup.py 完成設定
    echo.
    pause
    exit /b 1
)

echo ✅ 憑證檔案檢查完成

:: 執行程式
echo.
echo 🚀 開始執行主程式...
echo ==================================================
python sheets_processor.py

:: 檢查執行結果
if errorlevel 1 (
    echo.
    echo ❌ 程式執行失敗
    echo 請檢查錯誤訊息並修正問題
) else (
    echo.
    echo ✅ 程式執行完成
)

echo.
echo 按任意鍵結束...
pause >nul 