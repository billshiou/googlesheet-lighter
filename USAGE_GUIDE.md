# 使用指南 - Google Sheets 區塊瀏覽器資料自動處理工具

## 🚀 快速開始（5分鐘設定）

### 1. 下載並準備環境
```bash
# 確保已安裝 Python 3.8+
python --version

# 下載專案檔案到同一個資料夾
```

### 2. 設定 Google Sheets API
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案 → 啟用 Google Sheets API
3. 建立 OAuth 2.0 憑證 → 下載 `credentials.json`
4. 將 `credentials.json` 放在專案根目錄

### 3. 設定專案
```bash
# 複製設定檔
copy config_template.py config.py

# 編輯 config.py，填入您的 Google Sheets ID
```

### 4. 準備 Google Sheets
- 建立新的 Google Sheets
- 第二個分頁命名為「交易」
- 按照下方格式設定標題行

### 5. 執行工具
```bash
# Windows 用戶：雙擊 run.bat
# 其他用戶：python sheets_processor.py
```

## 📊 Google Sheets 格式要求

### 必要欄位（第二個分頁「交易」）
```
A: Name | B: Address | C: URL | D: Balance | E: Last Updated | F: Change | G: Collateral Amount
H: Open Positions1 | I: Symbol1 | J: Price1 | K: Size1 | L: Direction1 | M: Realized PnL1 | N: Unrealized PnL1
O: Open Positions2 | P: Symbol2 | Q: Price2 | R: Size2 | S: Direction2 | T: Realized PnL2 | U: Unrealized PnL2
```

### 範例資料
```
Name     Address  URL                 Balance  Last Updated         Change   Collateral Amount Open Positions1     Symbol1  Price1  Size1   Direction1 Realized PnL1 Unrealized PnL1 Open Positions2 Symbol2  Price2  Size2   Direction2 Realized PnL2 Unrealized PnL2
Account1 0x123... https://scan.lighter.xyz/account/53015 $1000     2024/01/01 12:00:00        $50       $500        BTC | Size: 0.1 | Side: Long  BTC     45000    0.1     Long      $100      $200     ETH | Size: 1.0 | Side: Short ETH     3000     1.0     Short     $50       $150
```

## 🔧 重要設定

### config.py 主要設定
```python
# 必填：您的 Google Sheets ID（從網址取得）
SPREADSHEET_ID = "1AzFHfAT65IA5p9BS-mMlEOeNRnCHNpAIdZNJ62L_-hY"

# 網址所在欄位（通常是 C 欄）
URL_COLUMN = "C"

# 開始處理行號（通常是第2行，第1行是標題）
START_ROW = 2
```

### 如何取得 Google Sheets ID
1. 開啟您的 Google Sheets
2. 從網址複製 ID：
   ```
   https://docs.google.com/spreadsheets/d/1AzFHfAT65IA5p9BS-mMlEOeNRnCHNpAIdZNJ62L_-hY/edit
   ```
   其中 `1AzFHfAT65IA5p9BS-mMlEOeNRnCHNpAIdZNJ62L_-hY` 就是 ID

## 🌐 支援的網址格式

| 平台 | 網址格式 |
|------|----------|
| **Lighter** | `https://scan.lighter.xyz/account/53015` |
| **Etherscan** | `https://etherscan.io/address/0x123...` |
| **BSCscan** | `https://bscscan.com/address/0x123...` |
| **Polygonscan** | `https://polygonscan.com/address/0x123...` |
| **Arbiscan** | `https://arbiscan.io/address/0x123...` |
| **Optimistic Etherscan** | `https://optimistic.etherscan.io/address/0x123...` |
| **Solscan** | `https://solscan.io/account/123...` |
| **Solana Explorer** | `https://explorer.solana.com/address/123...` |

## 🔄 自動化流程

### 執行步驟
1. **認證** → 2. **驗證欄位** → 3. **爬取資料** → 4. **查詢價格** → 5. **更新表格**

### 排程設定
- **預設**：每小時自動執行一次
- **立即執行**：啟動時立即執行一次
- **手動執行**：可隨時手動執行

## 🛠️ 常見問題

### 1. 認證失敗
**解決方案**：
- 檢查 `credentials.json` 檔案是否存在
- 確認 Google Sheets API 已啟用
- 重新下載憑證檔案

### 2. 欄位錯誤
**解決方案**：
- 確認第二個分頁名為「交易」
- 檢查標題行是否包含所有必要欄位
- 確認欄位順序正確

### 3. 網路錯誤
**解決方案**：
- 檢查網路連線
- 確認目標網站可達性
- 等待後重試

### 4. API 限制
**說明**：這是正常現象，程式會自動處理

## 📞 技術支援

- **查看完整說明**：[README.md](README.md)
- **查看更新日誌**：[CHANGELOG.md](CHANGELOG.md)
- **提交問題**：在 GitHub 上提交 Issue

---

**版本**: v1.2.0 | **更新日期**: 2024年7月 | **支援平台**: Windows, macOS, Linux 