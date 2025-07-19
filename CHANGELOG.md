# 更新日誌

## [1.0.0] - 2025-01-19

### 新增功能
- 🚀 初始版本發布
- 📊 支援從區塊瀏覽器網址自動爬取交易資料
- 💰 整合 CoinGecko API 自動獲取加密貨幣價格
- 🔄 支援批次處理和自動重試機制
- ⏰ 內建排程功能，支援每小時自動執行
- 🛡️ 安全機制，防止覆蓋重要欄位（如公式）

### 支援的區塊瀏覽器
- Lighter (scan.lighter.xyz)
- Etherscan
- BSCScan
- PolygonScan
- Arbiscan
- Optimistic Etherscan
- Solscan
- Solana Explorer

### 支援的資料欄位
- Address（錢包地址）
- Collateral Amount（抵押金額）
- Open Positions（開放倉位）
- Symbol（幣種代號）
- Price（當前價格）
- Size（倉位大小）
- Direction（交易方向）
- Realized PnL（已實現盈虧）
- Unrealized PnL（未實現盈虧）
- Last Updated（最後更新時間）

### 技術特色
- 🔒 硬編碼欄位位置，確保更新安全性
- 📝 詳細的日誌記錄和錯誤處理
- 🔄 自動重試和延遲機制
- 🎯 精確的資料提取和清理
- ⚡ 批次處理優化，減少 API 呼叫

### 檔案結構
```
├── sheets_processor.py      # 主程式
├── config_template.py       # 設定檔範本
├── coingecko_price_fetcher.py  # 價格查詢模組
├── setup.py                # 設定腳本
├── run.bat                 # Windows 批次執行檔
├── requirements.txt        # Python 依賴套件
├── README.md              # 使用說明
├── LICENSE                # 授權條款
├── .gitignore            # Git 忽略檔案
├── CHANGELOG.md          # 更新日誌
├── CONTRIBUTING.md       # 貢獻指南
├── credentials_template.json  # 憑證範本
└── coin_mapping.json     # 幣種映射檔
```

### 安裝與使用
1. 安裝 Python 3.8+ 和必要套件
2. 設定 Google Sheets API 憑證
3. 複製 `config_template.py` 為 `config.py` 並填入實際設定
4. 執行 `python sheets_processor.py` 或雙擊 `run.bat`

### 安全機制
- ✅ 只更新指定的安全欄位
- ✅ 驗證欄位名稱和位置
- ✅ 保護包含公式的欄位
- ✅ 詳細的更新日誌記錄

---

## 未來計劃

### 計劃中的功能
- 🔍 支援更多區塊瀏覽器
- 📈 歷史價格追蹤
- 🎨 自訂欄位映射介面
- 📱 Web 介面
- 🔔 通知功能（Email/Telegram）
- 📊 資料分析和報表

### 技術改進
- ⚡ 效能優化
- 🛡️ 更強的安全機制
- 📝 更詳細的錯誤處理
- 🔧 更靈活的配置選項 