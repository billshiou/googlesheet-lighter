# -*- coding: utf-8 -*-
"""
Google Sheets 區塊瀏覽器資料自動處理工具 - 設定檔範本

請複製此檔案為 config.py 並填入您的實際設定。
"""

# ============================================================================
# Google Sheets 設定
# ============================================================================

# Google Sheets 的 ID（從網址中取得）
# 例如：https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
# 其中 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms 就是 SPREADSHEET_ID
SPREADSHEET_ID = "your_spreadsheet_id_here"

# 區塊瀏覽器網址所在的欄位（使用字母表示）
URL_COLUMN = "C"

# 開始處理的行號（通常第1行是標題，所以從第2行開始）
START_ROW = 2

# 結束處理的行號（留空表示處理到最後一行）
END_ROW = None

# ============================================================================
# 目標欄位設定（硬編碼位置，確保安全）
# ============================================================================

# 硬編碼的欄位位置（0-based index）
# 這些位置是固定的，不會動態映射，確保不會覆蓋到其他欄位
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
    # 保持向後相容的欄位
    'symbol': 8,             # I欄：Symbol（與 Symbol1 相同）
    'price': 9,              # J欄：Price（與 Price1 相同）
    'size': 10,              # K欄：Size（與 Size1 相同）
    'direction': 11,         # L欄：Direction（與 Direction1 相同）
    'realized_pnl': 12,      # M欄：Realized PnL（與 Realized PnL1 相同）
    'unrealized_pnl': 13,    # N欄：Unrealized PnL（與 Unrealized PnL1 相同）
}

# 預期的欄位名稱（用於驗證）
EXPECTED_COLUMN_NAMES = {
    4: ['last updated', 'last_updated', '最後更新', '更新時間'],
    6: ['collateral amount', 'collateral', '抵押', '抵押金額'],
    7: ['open positions', 'open_positions', '開放倉位', '倉位'],
    # 第一組倉位
    8: ['symbol1', 'symbol', '幣種1', '代幣1', 'symbol'],
    9: ['price1', 'price', '價格1', 'current price'],
    10: ['size1', 'size', '大小1', '倉位大小1'],
    11: ['direction1', 'direction', '方向1', 'side1', '交易方向1'],
    12: ['realized pnl1', 'realized_pnl1', '已實現盈虧1'],
    13: ['unrealized pnl1', 'unrealized_pnl1', '未實現盈虧1'],
    # 第二組倉位
    14: ['symbol2', '幣種2', '代幣2'],
    15: ['price2', '價格2'],
    16: ['size2', '大小2', '倉位大小2'],
    17: ['direction2', '方向2', 'side2', '交易方向2'],
    18: ['realized pnl2', 'realized_pnl2', '已實現盈虧2'],
    19: ['unrealized pnl2', 'unrealized_pnl2', '未實現盈虧2'],
}

# ============================================================================
# 支援的區塊瀏覽器
# ============================================================================

SUPPORTED_EXPLORERS = {
    'lighter': {
        'base_url': 'scan.lighter.xyz',
        'patterns': [
            r'https?://scan\.lighter\.xyz/address/([a-zA-Z0-9]{42})',
            r'https?://scan\.lighter\.xyz/tx/([a-zA-Z0-9]{66})',
        ]
    },
    'etherscan': {
        'base_url': 'etherscan.io',
        'patterns': [
            r'https?://etherscan\.io/address/([a-zA-Z0-9]{42})',
            r'https?://etherscan\.io/tx/([a-zA-Z0-9]{66})',
        ]
    },
    'bscscan': {
        'base_url': 'bscscan.com',
        'patterns': [
            r'https?://bscscan\.com/address/([a-zA-Z0-9]{42})',
            r'https?://bscscan\.com/tx/([a-zA-Z0-9]{66})',
        ]
    },
    'polygonscan': {
        'base_url': 'polygonscan.com',
        'patterns': [
            r'https?://polygonscan\.com/address/([a-zA-Z0-9]{42})',
            r'https?://polygonscan\.com/tx/([a-zA-Z0-9]{66})',
        ]
    },
    'arbiscan': {
        'base_url': 'arbiscan.io',
        'patterns': [
            r'https?://arbiscan\.io/address/([a-zA-Z0-9]{42})',
            r'https?://arbiscan\.io/tx/([a-zA-Z0-9]{66})',
        ]
    },
    'optimistic_etherscan': {
        'base_url': 'optimistic.etherscan.io',
        'patterns': [
            r'https?://optimistic\.etherscan\.io/address/([a-zA-Z0-9]{42})',
            r'https?://optimistic\.etherscan\.io/tx/([a-zA-Z0-9]{66})',
        ]
    },
    'solscan': {
        'base_url': 'solscan.io',
        'patterns': [
            r'https?://solscan\.io/account/([a-zA-Z0-9]{32,44})',
            r'https?://solscan\.io/tx/([a-zA-Z0-9]{32,88})',
        ]
    },
    'solana_explorer': {
        'base_url': 'explorer.solana.com',
        'patterns': [
            r'https?://explorer\.solana\.com/address/([a-zA-Z0-9]{32,44})',
            r'https?://explorer\.solana\.com/tx/([a-zA-Z0-9]{32,88})',
        ]
    }
}

# ============================================================================
# API 設定
# ============================================================================

# CoinGecko API 設定
COINGECKO_API_BASE_URL = "https://api.coingecko.com/api/v3"
COINGECKO_API_DELAY = 1.2  # API 呼叫間隔（秒）
COINGECKO_MAX_RETRIES = 3  # 最大重試次數

# 批次處理設定
BATCH_SIZE = 10  # 批次更新的大小
BATCH_DELAY = 2  # 批次間隔（秒）

# 重試設定
MAX_RETRIES = 3  # 最大重試次數
RETRY_DELAY = 5  # 重試延遲（秒）

# ============================================================================
# 排程設定
# ============================================================================

# 是否啟用排程（每小時執行一次）
ENABLE_SCHEDULER = True

# 排程間隔（分鐘）
SCHEDULE_INTERVAL_MINUTES = 60

# 是否在啟動時立即執行一次
RUN_IMMEDIATELY = True

# ============================================================================
# 日誌設定
# ============================================================================

# 是否啟用詳細日誌
VERBOSE_LOGGING = True

# 日誌等級
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# ============================================================================
# 安全設定
# ============================================================================

# 是否啟用欄位驗證
ENABLE_COLUMN_VALIDATION = True

# 是否啟用安全模式（只更新指定欄位）
SAFE_MODE = True

# 危險欄位（絕對不會更新）
DANGEROUS_COLUMNS = ['交易', 'transaction', 'formula', '公式'] 