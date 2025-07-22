# 更新日誌

## [v1.1.0] - 2024-01-19

### ✨ 新增功能
- **多組倉位支援**：新增對兩組 Open Positions 的完整支援
- **獨立欄位管理**：每組倉位有獨立的 Symbol、Price、Size、Direction、PnL 欄位
- **向後相容性**：保持與原有單倉位格式的完全相容性

### 🔧 技術改進
- 更新 `scrape_block_explorer_data` 方法以支援兩組倉位資料提取
- 修改 `fill_prices_by_symbol` 方法以批次處理兩組倉位的價格查詢
- 更新欄位映射配置以支援新的欄位結構

### 📋 欄位結構更新
- **第一組倉位**：Symbol1 (I欄)、Price1 (J欄)、Size1 (K欄)、Direction1 (L欄)、Realized PnL1 (M欄)、Unrealized PnL1 (N欄)
- **第二組倉位**：Symbol2 (O欄)、Price2 (P欄)、Size2 (Q欄)、Direction2 (R欄)、Realized PnL2 (S欄)、Unrealized PnL2 (T欄)
- 保持原有欄位作為主要倉位（向後相容）

### 📚 文檔更新
- 更新 README.md 以反映新的兩組倉位功能
- 更新 config_template.py 以包含新的欄位映射
- 添加詳細的使用範例和欄位結構說明

### 🔒 安全性
- 保持原有的欄位驗證和安全機制
- 確保新欄位不會影響現有的安全設定

---

## [v1.0.0] - 2024-01-19

### 🎉 初始版本
- **自動資料爬取**：從區塊瀏覽器網址自動提取交易資料
- **智能價格查詢**：使用 CoinGecko API 自動獲取最新加密貨幣價格
- **安全欄位更新**：只更新指定欄位，保護其他欄位不被覆蓋
- **批次處理**：支援批次更新，減少 API 呼叫次數
- **錯誤重試機制**：自動重試失敗的請求，確保資料完整性
- **排程執行**：支援每小時自動執行

### 🔧 核心功能
- 支援多個區塊瀏覽器（Lighter、Etherscan、BSCscan 等）
- 智能資料解析和清理
- Google Sheets API 整合
- 完整的錯誤處理和日誌記錄

### 📋 支援的欄位
- Address、Collateral Amount、Open Positions
- Symbol、Price、Size、Direction
- Realized PnL、Unrealized PnL
- Last Updated

### 🛠️ 技術特色
- Python 3.8+ 支援
- 安全的 Google API 認證流程
- 硬編碼欄位位置確保安全性
- 詳細的執行日誌和錯誤報告 