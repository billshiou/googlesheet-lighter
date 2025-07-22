# Google Sheets 區塊瀏覽器資料自動處理工具

一個自動化工具，用於從區塊瀏覽器網址爬取資料並更新 Google Sheets，支援多組倉位管理和即時價格查詢。

## ✨ 主要功能

### 🔄 自動資料爬取
- **多區塊瀏覽器支援**：Lighter、Etherscan、BSCscan、Polygonscan、Arbiscan、Optimistic Etherscan、Solscan、Solana Explorer
- **智能資料解析**：自動提取地址、餘額、抵押金額、倉位資訊等
- **重試機制**：網路錯誤時自動重試，確保資料完整性

### 📊 多組倉位管理
- **雙倉位支援**：同時管理兩組 Open Positions
- **獨立欄位**：每組倉位有獨立的 Symbol、Price、Size、Direction、PnL 欄位
- **向後相容**：保持與原有單倉位格式的相容性

### 💰 即時價格查詢
- **CoinGecko API 整合**：獲取即時加密貨幣價格
- **批次處理**：高效批次查詢，減少 API 呼叫次數
- **智能延遲**：避免 API 限制，確保穩定運行

### 🔒 安全與驗證
- **欄位驗證**：自動驗證 Google Sheets 欄位結構
- **安全模式**：只更新指定欄位，避免意外覆蓋
- **憑證管理**：安全的 Google API 認證流程

## 📋 支援的欄位結構

### 基本資訊欄位
- **Last Updated** (E欄)：最後更新時間
- **Collateral Amount** (G欄)：抵押金額
- **Open Positions** (H欄)：倉位摘要資訊

### 第一組倉位欄位
- **Symbol1** (I欄)：幣種代號
- **Price1** (J欄)：當前價格
- **Size1** (K欄)：倉位大小
- **Direction1** (L欄)：交易方向
- **Realized PnL1** (M欄)：已實現盈虧
- **Unrealized PnL1** (N欄)：未實現盈虧

### 第二組倉位欄位
- **Symbol2** (O欄)：幣種代號
- **Price2** (P欄)：當前價格
- **Size2** (Q欄)：倉位大小
- **Direction2** (R欄)：交易方向
- **Realized PnL2** (S欄)：已實現盈虧
- **Unrealized PnL2** (T欄)：未實現盈虧

## 🚀 快速開始

### 1. 環境準備
```bash
# 安裝 Python 3.8+
# 下載專案檔案
```

### 2. 安裝依賴
```bash
pip install -r requirements.txt
```

### 3. 設定 Google Sheets API
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Sheets API
4. 建立服務帳號並下載 `credentials.json`
5. 將 `credentials.json` 放在專案根目錄

### 4. 設定專案
1. 複製 `config_template.py` 為 `config.py`
2. 編輯 `config.py`，填入您的 Google Sheets ID 和欄位設定
3. 確保您的 Google Sheets 有正確的欄位結構

### 5. 執行工具
```bash
# Windows
run.bat

# 或直接執行
python sheets_processor.py
```

## ⚙️ 設定說明

### Google Sheets 設定
```python
# Google Sheets 的 ID（從網址中取得）
SPREADSHEET_ID = "your_spreadsheet_id_here"

# 區塊瀏覽器網址所在的欄位
URL_COLUMN = "C"

# 開始和結束處理的行號
START_ROW = 2
END_ROW = None  # None 表示處理到最後一行
```

### 欄位映射設定
```python
# 硬編碼的欄位位置（0-based index）
COLUMN_MAPPINGS = {
    'last_updated': 4,       # E欄：Last Updated
    'collateral_amount': 6,  # G欄：Collateral Amount
    'open_positions': 7,     # H欄：Open Positions
    # 第一組倉位
    'symbol1': 8,            # I欄：Symbol1
    'price1': 9,             # J欄：Price1
    'size1': 10,             # K欄：Size1
    'direction1': 11,        # L欄：Direction1
    'realized_pnl1': 12,     # M欄：Realized PnL1
    'unrealized_pnl1': 13,   # N欄：Unrealized PnL1
    # 第二組倉位
    'symbol2': 14,           # O欄：Symbol2
    'price2': 15,            # P欄：Price2
    'size2': 16,             # Q欄：Size2
    'direction2': 17,        # R欄：Direction2
    'realized_pnl2': 18,     # S欄：Realized PnL2
    'unrealized_pnl2': 19,   # T欄：Unrealized PnL2
}
```

## 📝 使用範例

### Google Sheets 結構範例
```
A        B        C                    D        E                    F        G                H                    I        J       K       L        M            N               O        P       Q       R        S            T
Name     Address  URL                 Balance  Last Updated         Change   Collateral Amount Open Positions      Symbol1  Price1  Size1   Direction1 Realized PnL1 Unrealized PnL1 Symbol2  Price2  Size2   Direction2 Realized PnL2 Unrealized PnL2
Account1 0x123... https://scan.lighter.xyz/account/53015 $1000     2024/01/01 12:00:00        $50       $500        BTC | Size: 0.1 | Side: Long  BTC     45000    0.1     Long      $100      $200     ETH     3000     1.0     Short     $50       $150
```

### 支援的網址格式
- **Lighter**: `https://scan.lighter.xyz/account/53015`
- **Etherscan**: `https://etherscan.io/address/0x123...`
- **BSCscan**: `https://bscscan.com/address/0x123...`
- **Polygonscan**: `https://polygonscan.com/address/0x123...`
- **Arbiscan**: `https://arbiscan.io/address/0x123...`
- **Optimistic Etherscan**: `https://optimistic.etherscan.io/address/0x123...`
- **Solscan**: `https://solscan.io/account/123...`
- **Solana Explorer**: `https://explorer.solana.com/address/123...`

## 🔄 自動化流程

### 執行步驟
1. **認證檢查**：驗證 Google Sheets API 憑證
2. **欄位驗證**：檢查 Google Sheets 欄位結構
3. **資料爬取**：從區塊瀏覽器網址爬取資料
4. **價格查詢**：批次查詢所有幣種的即時價格
5. **資料更新**：將爬取和查詢的資料更新到 Google Sheets

### 排程執行
- **預設排程**：每小時自動執行一次
- **立即執行**：啟動時立即執行一次
- **手動執行**：可隨時手動執行

## 🛠️ 故障排除

### 常見問題
1. **認證失敗**：檢查 `credentials.json` 檔案和 Google Sheets 權限
2. **欄位錯誤**：確認 Google Sheets 欄位結構與設定一致
3. **網路錯誤**：檢查網路連線和目標網站可達性
4. **API 限制**：CoinGecko API 有速率限制，程式會自動處理

### 日誌查看
程式會輸出詳細的執行日誌，包括：
- 認證狀態
- 欄位驗證結果
- 爬取進度
- 價格查詢結果
- 更新狀態

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

詳見 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📞 支援

如有問題或建議，請：
1. 查看 [CHANGELOG.md](CHANGELOG.md) 了解最新更新
2. 提交 GitHub Issue
3. 檢查故障排除章節

---

**版本**: v1.1.0  
**更新日期**: 2024年1月  
**支援平台**: Windows, macOS, Linux 