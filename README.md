# Google Sheets 區塊瀏覽器資料自動處理工具

這是一個自動化工具，用於從區塊瀏覽器網址爬取資料並更新 Google Sheets，同時自動獲取加密貨幣價格。

## 🚀 功能特色

- **自動爬取區塊瀏覽器資料**：從 Lighter 等區塊瀏覽器網址自動提取交易資料
- **智能價格查詢**：使用 CoinGecko API 自動獲取最新加密貨幣價格
- **安全欄位更新**：只更新指定欄位，保護其他欄位（如公式）不被覆蓋
- **批次處理**：支援批次更新，減少 API 呼叫次數
- **錯誤重試機制**：自動重試失敗的請求，確保資料完整性
- **排程執行**：支援每小時自動執行

## 📋 支援的資料欄位

| 欄位 | 說明 | 範例 |
|------|------|------|
| Address | 錢包地址 | 0x40b1fE8775A7663E14A4a46D922237C0A941002E |
| Collateral Amount | 抵押金額 | 519.89 |
| Open Positions | 開放倉位資訊 | BTC \| Size: 0.5 \| Side: LONG |
| Symbol | 幣種代號 | BTC, ETH, AVAX |
| Size | 倉位大小 | 0.5 |
| Direction | 交易方向 | LONG, SHORT |
| Realized PnL | 已實現盈虧 | 123.45 |
| Unrealized PnL | 未實現盈虧 | -67.89 |
| Price | 當前價格 | 23456.78 |
| Last Updated | 最後更新時間 | 2025/01/19 12:34:56 |

## 🛠️ 安裝與設定

### 1. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 2. Google Sheets API 設定

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Sheets API
4. 建立服務帳戶並下載 `credentials.json`
5. 將 `credentials.json` 放在專案根目錄

### 3. 設定 Google Sheets

1. 建立新的 Google Sheets
2. 設定表頭欄位（參考下方格式）
3. 在 `config.py` 中設定 Spreadsheet ID

### 4. 設定 config.py

1. **複製設定範本**：
   ```bash
   cp config_template.py config.py
   ```

2. **編輯 config.py**：
   ```python
   # Google Sheets 設定
   SPREADSHEET_ID = "your_spreadsheet_id_here"  # 填入您的實際 Spreadsheet ID
   
   # 區塊瀏覽器網址所在的欄位
   URL_COLUMN = "C"
   
   # 開始處理的行號（通常第1行是標題，所以從第2行開始）
   START_ROW = 2
   
   # 結束處理的行號（留空表示處理到最後一行）
   END_ROW = None
   ```

**重要**：請確保 `config.py` 包含您的實際 Spreadsheet ID，但不要將此檔案上傳到公開的版本控制系統。

## 📊 Google Sheets 格式

請確保您的 Google Sheets 有以下欄位結構：

| A | B | C | D | E | F | G | H | I | J | K | L | M | N | O | P | Q |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 指紋編號 | 資金源 | 區塊瀏覽器 | 交易 | Address | Collateral Amount | (空) | Open Positions | Last Updated | Symbol | Price | Size | Direction | Realized PnL | Unrealized PnL | 倉位小計 | 帳戶未使用餘額 |

## 🚀 使用方法

### 快速開始

```bash
python sheets_processor.py
```

### 批次檔案執行（Windows）

```bash
run.bat
```

### 手動設定

```bash
python setup.py
```

## ⚙️ 進階設定

### 支援的區塊瀏覽器

- Lighter (scan.lighter.xyz)
- Etherscan
- BSCScan
- PolygonScan
- Arbiscan
- Optimistic Etherscan
- Solscan
- Solana Explorer

### 支援的加密貨幣

支援 CoinGecko 上的所有主要加密貨幣，包括：
- BTC, ETH, AVAX, TON, KAITO
- 以及更多...

### 自訂欄位映射

在 `config.py` 中可以自訂欄位映射：

```python
TARGET_COLUMNS = {
    'address': ['address', '地址', '錢包地址'],
    'collateral_amount': ['collateral', '抵押', '抵押金額'],
    'symbol': ['symbol', '幣種', '代幣'],
    # ... 更多欄位
}
```

## 🔒 安全機制

- **硬編碼欄位位置**：使用固定的欄位索引，避免錯誤映射
- **欄位驗證**：檢查欄位名稱是否正確
- **白名單機制**：只更新指定的安全欄位
- **詳細日誌**：清楚顯示每個更新操作

## 📝 日誌說明

程式執行時會顯示詳細的日誌：

```
==================================================
Google Sheets 自動處理程式
==================================================
啟動時間: 2025-01-19 12:00:00
排程設定: 每個整點自動執行

立即執行第一次...

=== 步驟1：填寫 symbol/基本資料 ===
驗證欄位位置:
  E: Address -> address
  F: Collateral Amount -> collateral_amount
  H: Open Positions -> open_positions
  ...

=== 步驟2：根據 symbol 批次查價並填入 Price ===
找到的幣種: ['KAITO', 'AVAX', 'TON']
查價結果:
  KAITO: $1.65
  AVAX: $23.79
  TON: $3.25
```

## 🐛 故障排除

### 常見問題

1. **認證錯誤**
   - 檢查 `credentials.json` 是否正確
   - 確認 Google Sheets API 已啟用

2. **欄位映射錯誤**
   - 確認 Google Sheets 表頭格式正確
   - 檢查 `config.py` 中的設定

3. **價格查詢失敗**
   - 檢查網路連線
   - 確認幣種代號正確

4. **API 配額限制**
   - 程式會自動重試並延遲
   - 考慮降低更新頻率

### 錯誤代碼

- `429`: API 配額限制，程式會自動重試
- `401`: 認證失敗，檢查 credentials.json
- `404`: Spreadsheet 不存在，檢查 SPREADSHEET_ID

## 📄 授權

本專案採用 MIT 授權條款。

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📞 支援

如有問題，請在 GitHub 上提交 Issue。

---

**注意**：請確保您的 Google Sheets 有適當的權限設定，並且不要將以下敏感檔案上傳到公開的版本控制系統：
- `credentials.json`（Google Sheets API 憑證）
- `config.py`（包含您的實際 Spreadsheet ID）
- `token.pickle`（認證 token） 