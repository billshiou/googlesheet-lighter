#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Sheets 區塊瀏覽器資料自動處理工具 - 設定腳本

此腳本會檢查您的環境設定並提供詳細的安裝指南。
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_header():
    """印出標題"""
    print("=" * 60)
    print("Google Sheets 區塊瀏覽器資料自動處理工具 - 設定腳本")
    print("=" * 60)
    print()

def check_python_version():
    """檢查 Python 版本"""
    print("🔍 檢查 Python 版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 錯誤：需要 Python 3.8 或更高版本")
        print(f"   當前版本：{version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python 版本：{version.major}.{version.minor}.{version.micro}")
        return True

def install_requirements():
    """安裝必要的套件"""
    print("\n📦 安裝必要的套件...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 套件安裝完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 套件安裝失敗：{e}")
        return False

def check_credentials():
    """檢查 credentials.json 檔案"""
    print("\n🔐 檢查 Google Sheets API 憑證...")
    
    if os.path.exists("credentials.json"):
        print("✅ 找到 credentials.json 檔案")
        try:
            with open("credentials.json", "r", encoding="utf-8") as f:
                creds = json.load(f)
            if "type" in creds and creds["type"] == "service_account":
                print("✅ 憑證格式正確（服務帳戶）")
                return True
            else:
                print("⚠️  憑證格式可能不正確，請確認是服務帳戶憑證")
                return False
        except json.JSONDecodeError:
            print("❌ credentials.json 格式錯誤")
            return False
    else:
        print("❌ 找不到 credentials.json 檔案")
        return False

def check_config():
    """檢查 config.py 設定"""
    print("\n⚙️  檢查 config.py 設定...")
    
    if not os.path.exists("config.py"):
        print("❌ 找不到 config.py 檔案")
        print("請先複製 config_template.py 為 config.py 並填入您的設定")
        return False
    
    try:
        import config
        print("✅ config.py 載入成功")
        
        # 檢查必要的設定
        required_settings = [
            "SPREADSHEET_ID",
            "URL_COLUMN", 
            "START_ROW"
        ]
        
        for setting in required_settings:
            if hasattr(config, setting):
                value = getattr(config, setting)
                if value:
                    print(f"✅ {setting}: {value}")
                else:
                    print(f"⚠️  {setting}: 未設定")
            else:
                print(f"❌ {setting}: 未定義")
        
        return True
    except ImportError as e:
        print(f"❌ config.py 載入失敗：{e}")
        return False

def create_credentials_template():
    """建立 credentials.json 範本"""
    print("\n📝 建立 credentials.json 範本...")
    
    template = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
    }
    
    with open("credentials_template.json", "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print("✅ credentials_template.json 已建立")

def print_setup_instructions():
    """印出設定說明"""
    print("\n" + "=" * 60)
    print("📋 設定說明")
    print("=" * 60)
    
    print("\n1️⃣  Google Cloud Console 設定：")
    print("   a) 前往 https://console.cloud.google.com/")
    print("   b) 建立新專案或選擇現有專案")
    print("   c) 啟用 Google Sheets API")
    print("   d) 建立服務帳戶")
    print("   e) 下載 JSON 憑證檔案")
    print("   f) 重新命名為 credentials.json")
    print("   g) 放在專案根目錄")
    
    print("\n2️⃣  Google Sheets 設定：")
    print("   a) 建立新的 Google Sheets")
    print("   b) 設定表頭欄位（參考 README.md）")
    print("   c) 取得 Spreadsheet ID（從網址中複製）")
    print("   d) 複製 config_template.py 為 config.py")
    print("   e) 在 config.py 中設定 SPREADSHEET_ID")
    print("   f) 將服務帳戶 email 加入編輯者權限")
    
    print("\n3️⃣  執行測試：")
    print("   python sheets_processor.py")
    
    print("\n4️⃣  排程執行（可選）：")
    print("   python -c \"import sheets_processor; sheets_processor.run_main_process()\"")

def print_troubleshooting():
    """印出故障排除說明"""
    print("\n" + "=" * 60)
    print("🔧 故障排除")
    print("=" * 60)
    
    print("\n常見問題：")
    print("1. 認證錯誤：檢查 credentials.json 是否正確")
    print("2. 權限錯誤：確認服務帳戶有編輯 Google Sheets 的權限")
    print("3. API 配額限制：程式會自動重試，請耐心等待")
    print("4. 欄位映射錯誤：確認 Google Sheets 表頭格式正確")
    print("5. 網路連線問題：檢查網路連線和防火牆設定")

def main():
    """主函數"""
    print_header()
    
    # 檢查 Python 版本
    if not check_python_version():
        print("\n❌ 請升級 Python 版本後再試")
        return
    
    # 安裝套件
    if not install_requirements():
        print("\n❌ 套件安裝失敗，請檢查網路連線")
        return
    
    # 檢查憑證
    creds_ok = check_credentials()
    if not creds_ok:
        print("\n⚠️  憑證設定不完整")
        create_credentials_template()
    
    # 檢查設定
    config_ok = check_config()
    
    # 印出說明
    print_setup_instructions()
    
    if not creds_ok or not config_ok:
        print("\n⚠️  請完成上述設定後再執行主程式")
    else:
        print("\n✅ 設定檢查完成！可以執行主程式了")
    
    print_troubleshooting()
    
    print("\n" + "=" * 60)
    print("🎉 設定腳本執行完成")
    print("=" * 60)

if __name__ == "__main__":
    main() 