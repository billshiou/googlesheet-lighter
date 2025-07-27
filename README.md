# Google Sheets 區塊瀏覽器資料自動處理工具

一個自動化工具，用於從區塊瀏覽器網址爬取資料並更新 Google Sheets，支援多組倉位管理和即時價格查詢。

## 📚 文件導覽

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - 5分鐘快速開始指南
- **[FILES.md](FILES.md)** - 詳細檔案清單說明
- **[CHANGELOG.md](CHANGELOG.md)** - 版本更新日誌
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - 貢獻指南

## 📁 專案檔案結構

```
整理lighter/
├── 📄 sheets_processor.py      # 主程式檔案
├── 📄 config.py               # 設定檔（需要自行建立）
├── 📄 config_template.py      # 設定檔範本
├── 📄 coingecko_price_fetcher.py  # CoinGecko 價格查詢模組
├── 📄 requirements.txt        # Python 依賴套件清單
├── 📄 run.bat                # Windows 快速啟動腳本
├── 📄 setup.py               # 初始設定工具
├── 📄 credentials_template.json  # Google API 憑證範本
├── 📄 coin_mapping.json      # 幣種對應表
├── 📄 README.md              # 使用說明（本檔案）
├── 📄 CHANGELOG.md           # 更新日誌
├── 📄 CONTRIBUTING.md        # 貢獻指南
├── 📄 LICENSE                # 授權條款
└── 📄 .gitignore             # Git 忽略檔案清單
```

## 🚀 快速開始指南

### 步驟 1：環境準備
1. **安裝 Python 3.8 或更高版本**
   - 下載網址：https://www.python.org/downloads/
   - 安裝時請勾選 "Add Python to PATH"

2. **下載專案檔案**
   - 將所有檔案下載到同一個資料夾
   - 確保檔案結構完整

### 步驟 2：Google Sheets API 設定
1. **前往 Google Cloud Console**
   - 網址：https://console.cloud.google.com/
   - 建立新專案或選擇現有專案

2. **啟用 Google Sheets API**
   - 在左側選單選擇 "API 和服務" > "程式庫"
   - 搜尋 "Google Sheets API" 並啟用

3. **建立憑證**
   - 前往 "API 和服務" > "憑證"
   - 點擊 "建立憑證" > "OAuth 2.0 用戶端 ID"
   - 選擇 "桌面應用程式"
   - 下載 JSON 檔案並重新命名為 `credentials.json`
   - 將檔案放在專案根目錄

### 步驟 3：專案設定
1. **複製設定檔**
   ```bash
   # 複製設定檔範本
   copy config_template.py config.py
   ```

2. **編輯 config.py**
   - 開啟 `config.py` 檔案
   - 修改 `SPREADSHEET_ID` 為您的 Google Sheets ID
   - 確認其他設定符合您的需求

3. **準備 Google Sheets**
   - 建立新的 Google Sheets 或使用現有的
   - 確保有第二個分頁名為「交易」
   - 按照下方欄位結構設定標題行

### 步驟 4：執行工具

#### 方法一：使用 Windows 批次檔（推薦）
```bash
# 雙擊執行
run.bat
```

#### 方法二：手動執行
```bash
# 安裝依賴套件
pip install -r requirements.txt

# 執行程式
python sheets_processor.py
```

## 📊 Google Sheets 欄位結構

### 必要欄位設定
您的 Google Sheets 第二個分頁「交易」需要包含以下欄位：

| 欄位 | 欄位名稱 | 說明 |
|------|----------|------|
| A | Name | 帳戶名稱 |
| B | Address | 錢包地址 |
| C | URL | 區塊瀏覽器網址 |
| D | Balance | 餘額 |
| E | Last Updated | 最後更新時間 |
| F | Change | 變化金額 |
| G | Collateral Amount | 抵押金額 |
| H | Open Positions1 | 第一組倉位摘要 |
| I | Symbol1 | 第一組幣種代號 |
| J | Price1 | 第一組當前價格 |
| K | Size1 | 第一組倉位大小 |
| L | Direction1 | 第一組交易方向 |
| M | Realized PnL1 | 第一組已實現盈虧 |
| N | Unrealized PnL1 | 第一組未實現盈虧 |
| O | Open Positions2 | 第二組倉位摘要 |
| P | Symbol2 | 第二組幣種代號 |
| Q | Price2 | 第二組當前價格 |
| R | Size2 | 第二組倉位大小 |
| S | Direction2 | 第二組交易方向 |
| T | Realized PnL2 | 第二組已實現盈虧 |
| U | Unrealized PnL2 | 第二組未實現盈虧 |

### 範例資料
```
Name     Address  URL                 Balance  Last Updated         Change   Collateral Amount Open Positions1     Symbol1  Price1  Size1   Direction1 Realized PnL1 Unrealized PnL1 Open Positions2 Symbol2  Price2  Size2   Direction2 Realized PnL2 Unrealized PnL2
Account1 0x123... https://scan.lighter.xyz/account/53015 $1000     2024/01/01 12:00:00        $50       $500        BTC | Size: 0.1 | Side: Long  BTC     45000    0.1     Long      $100      $200     ETH | Size: 1.0 | Side: Short ETH     3000     1.0     Short     $50       $150
```

## 🔧 設定檔說明

### 主要設定參數
```python
# Google Sheets 設定
SPREADSHEET_ID = "your_spreadsheet_id_here"  # 從網址中取得
URL_COLUMN = "C"                             # 網址所在欄位
START_ROW = 2                                # 開始處理行號
END_ROW = None                               # 結束處理行號（None=處理到最後）

# 排程設定
ENABLE_SCHEDULER = True                      # 是否啟用自動排程
SCHEDULE_INTERVAL_MINUTES = 60               # 排程間隔（分鐘）
RUN_IMMEDIATELY = True                       # 啟動時是否立即執行
```

### 如何取得 Google Sheets ID
1. 開啟您的 Google Sheets
2. 從網址中複製 ID：
   ```
   https://docs.google.com/spreadsheets/d/1AzFHfAT65IA5p9BS-mMlEOeNRnCHNpAIdZNJ62L_-hY/edit
   ```
   其中 `1AzFHfAT65IA5p9BS-mMlEOeNRnCHNpAIdZNJ62L_-hY` 就是 SPREADSHEET_ID

## 🌐 支援的區塊瀏覽器

| 平台 | 網址格式 | 範例 |
|------|----------|------|
| **Lighter** | `https://scan.lighter.xyz/account/53015` | 主要支援平台 |
| **Etherscan** | `https://etherscan.io/address/0x123...` | Ethereum 主網 |
| **BSCscan** | `https://bscscan.com/address/0x123...` | BSC 網路 |
| **Polygonscan** | `https://polygonscan.com/address/0x123...` | Polygon 網路 |
| **Arbiscan** | `https://arbiscan.io/address/0x123...` | Arbitrum 網路 |
| **Optimistic Etherscan** | `https://optimistic.etherscan.io/address/0x123...` | Optimism 網路 |
| **Solscan** | `https://solscan.io/account/123...` | Solana 網路 |
| **Solana Explorer** | `https://explorer.solana.com/address/123...` | Solana 官方瀏覽器 |

## ⚙️ 進階設定

### 自訂欄位位置
如果您需要修改欄位位置，請編輯 `config.py` 中的 `COLUMN_MAPPINGS`：

```python
COLUMN_MAPPINGS = {
    'last_updated': 4,       # E欄：Last Updated
    'collateral_amount': 6,  # G欄：Collateral Amount
    'symbol': 8,             # I欄：Symbol1
    'price': 9,              # J欄：Price1
    # ... 其他欄位
}
```

### API 設定調整
```python
# CoinGecko API 設定
COINGECKO_API_DELAY = 1.2    # API 呼叫間隔（秒）
COINGECKO_MAX_RETRIES = 3    # 最大重試次數

# 批次處理設定
BATCH_SIZE = 10              # 批次更新大小
BATCH_DELAY = 2              # 批次間隔（秒）
```

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

### 常見問題與解決方案

#### 1. 認證失敗
**問題**：`認證失敗: [錯誤訊息]`
**解決方案**：
- 檢查 `credentials.json` 檔案是否存在
- 確認 Google Sheets API 已啟用
- 重新下載憑證檔案

#### 2. 欄位錯誤
**問題**：`欄位驗證失敗，停止執行`
**解決方案**：
- 確認 Google Sheets 欄位結構與設定一致
- 檢查第二個分頁是否名為「交易」
- 確認標題行包含所有必要欄位

#### 3. 網路錯誤
**問題**：`網路錯誤 (嘗試 X/3)`
**解決方案**：
- 檢查網路連線
- 確認目標網站可達性
- 等待一段時間後重試

#### 4. API 限制
**問題**：`API配額限制，等待 X 秒後重試`
**解決方案**：
- 這是正常現象，程式會自動處理
- 如需更頻繁的更新，可調整 `COINGECKO_API_DELAY`

### 日誌查看
程式會輸出詳細的執行日誌，包括：
- ✅ 認證狀態
- ✅ 欄位驗證結果
- ✅ 爬取進度
- ✅ 價格查詢結果
- ✅ 更新狀態

## 📞 技術支援

### 取得協助
1. **查看更新日誌**：[CHANGELOG.md](CHANGELOG.md)
2. **提交 Issue**：在 GitHub 上提交問題
3. **檢查故障排除**：查看上方故障排除章節

### 系統需求
- **作業系統**：Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python 版本**：3.8 或更高版本
- **記憶體**：至少 512MB 可用記憶體
- **網路**：穩定的網際網路連線

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！詳見 [CONTRIBUTING.md](CONTRIBUTING.md)

---

**版本**: v1.2.0  
**更新日期**: 2024年7月  
**支援平台**: Windows, macOS, Linux  
**開發者**: 區塊瀏覽器資料處理工具團隊 