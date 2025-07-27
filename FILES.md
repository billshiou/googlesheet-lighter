# 檔案清單說明

## 📁 專案檔案結構與說明

### 🔧 核心程式檔案

#### `sheets_processor.py` - 主程式檔案
- **作用**：主要的資料處理程式
- **功能**：
  - Google Sheets API 認證與操作
  - 區塊瀏覽器資料爬取
  - 即時價格查詢與更新
  - 自動排程執行
- **重要程度**：⭐⭐⭐⭐⭐（核心檔案）

#### `coingecko_price_fetcher.py` - 價格查詢模組
- **作用**：CoinGecko API 價格查詢功能
- **功能**：
  - 批次查詢多個幣種價格
  - API 限制處理
  - 重試機制
- **重要程度**：⭐⭐⭐⭐（重要模組）

### ⚙️ 設定檔案

#### `config.py` - 主要設定檔
- **作用**：專案的主要設定檔案
- **包含**：
  - Google Sheets ID
  - 欄位映射設定
  - API 設定
  - 排程設定
- **重要程度**：⭐⭐⭐⭐⭐（必須設定）

#### `config_template.py` - 設定檔範本
- **作用**：提供設定檔範本
- **使用方式**：複製此檔案為 `config.py` 後進行修改
- **重要程度**：⭐⭐⭐（參考用）

#### `credentials_template.json` - Google API 憑證範本
- **作用**：Google API 憑證檔案範本
- **使用方式**：參考此檔案格式建立自己的 `credentials.json`
- **重要程度**：⭐⭐⭐（參考用）

### 📦 依賴與安裝檔案

#### `requirements.txt` - Python 依賴套件清單
- **作用**：列出所有需要的 Python 套件
- **使用方式**：`pip install -r requirements.txt`
- **重要程度**：⭐⭐⭐⭐（安裝必需）

#### `setup.py` - 初始設定工具
- **作用**：協助使用者完成初始設定
- **功能**：
  - 檢查環境
  - 安裝依賴
  - 設定憑證
- **重要程度**：⭐⭐⭐（輔助工具）

#### `run.bat` - Windows 快速啟動腳本
- **作用**：Windows 用戶的快速啟動腳本
- **功能**：
  - 檢查環境
  - 安裝依賴
  - 執行程式
- **重要程度**：⭐⭐⭐（Windows 用戶便利工具）

### 📊 資料檔案

#### `coin_mapping.json` - 幣種對應表
- **作用**：幣種代號對應表
- **功能**：協助正確識別和查詢幣種價格
- **重要程度**：⭐⭐⭐（資料支援）

### 📚 說明文件

#### `README.md` - 完整使用說明
- **作用**：專案的完整使用說明
- **內容**：
  - 功能介紹
  - 安裝指南
  - 設定說明
  - 故障排除
- **重要程度**：⭐⭐⭐⭐⭐（必讀文件）

#### `USAGE_GUIDE.md` - 快速使用指南
- **作用**：簡潔的使用指南
- **內容**：5分鐘快速開始指南
- **重要程度**：⭐⭐⭐⭐（快速參考）

#### `FILES.md` - 檔案清單說明（本檔案）
- **作用**：詳細說明每個檔案的作用
- **重要程度**：⭐⭐⭐（參考用）

#### `CHANGELOG.md` - 更新日誌
- **作用**：記錄版本更新內容
- **重要程度**：⭐⭐⭐（版本追蹤）

#### `CONTRIBUTING.md` - 貢獻指南
- **作用**：說明如何貢獻程式碼
- **重要程度**：⭐⭐（開發者參考）

#### `LICENSE` - 授權條款
- **作用**：專案的授權條款
- **重要程度**：⭐⭐（法律文件）

### 🔒 安全與系統檔案

#### `.gitignore` - Git 忽略檔案清單
- **作用**：指定 Git 不追蹤的檔案
- **包含**：
  - 憑證檔案
  - 快取檔案
  - 系統檔案
- **重要程度**：⭐⭐（版本控制）

#### `token.pickle` - Google API 認證快取
- **作用**：儲存 Google API 認證資訊
- **生成**：程式執行時自動生成
- **重要程度**：⭐⭐（認證快取）

## 📋 檔案重要性分類

### 🔴 核心檔案（必須存在）
- `sheets_processor.py`
- `config.py`
- `requirements.txt`
- `README.md`

### 🟡 重要檔案（建議存在）
- `coingecko_price_fetcher.py`
- `credentials.json`（需要自行建立）
- `USAGE_GUIDE.md`

### 🟢 輔助檔案（可選）
- `run.bat`（Windows 用戶）
- `setup.py`
- `coin_mapping.json`
- 其他說明文件

## 🚀 快速開始檔案清單

### 最小必要檔案
```
整理lighter/
├── sheets_processor.py      # 主程式
├── config.py               # 設定檔
├── requirements.txt        # 依賴清單
├── credentials.json        # Google API 憑證
└── README.md              # 使用說明
```

### 完整檔案清單
```
整理lighter/
├── sheets_processor.py
├── coingecko_price_fetcher.py
├── config.py
├── config_template.py
├── requirements.txt
├── run.bat
├── setup.py
├── credentials_template.json
├── coin_mapping.json
├── README.md
├── USAGE_GUIDE.md
├── FILES.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── .gitignore
```

## 📝 檔案命名規範

### 程式檔案
- 使用小寫字母和底線
- 例如：`sheets_processor.py`

### 設定檔案
- 使用小寫字母和底線
- 例如：`config.py`, `credentials.json`

### 說明文件
- 使用大寫字母和底線
- 例如：`README.md`, `USAGE_GUIDE.md`

### 批次檔案
- 使用小寫字母和點
- 例如：`run.bat`

---

**最後更新**：2024年7月  
**版本**：v1.2.0 