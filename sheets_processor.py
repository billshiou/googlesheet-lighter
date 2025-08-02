import os
import re
import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import asyncio
import threading
from datetime import datetime
import config

from coingecko_price_fetcher import CoinGeckoPriceFetcher

class CoinGeckoPriceFetcherWrapper:
    def __init__(self):
        self.coingecko_fetcher = CoinGeckoPriceFetcher()
        
    def get_current_price_rest(self, symbol: str) -> Optional[float]:
        """使用 CoinGecko API 獲取當前價格"""
        return self.coingecko_fetcher.get_single_price(symbol)

    def get_prices_for_symbols(self, symbols: List[str]) -> Dict[str, float]:
        """為多個幣種獲取價格（使用批次查詢）"""
        return self.coingecko_fetcher.get_batch_prices_with_delay(symbols, delay=3.0)

class SheetsProcessor:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.creds = None
        self.service = None
        self.price_fetcher = CoinGeckoPriceFetcherWrapper()

    def clean_monetary_value(self, value):
        """強力清理金額值，移除$、全形$、非數字、只留數字/小數/負號"""
        if not value:
            return value
        value_str = str(value)
        value_str = value_str.replace('$', '').replace('＄', '').strip()
        cleaned = re.sub(r'[^\d\-\.]', '', value_str)
        if cleaned.count('.') > 1:
            parts = cleaned.split('.')
            cleaned = parts[0] + '.' + ''.join(parts[1:])
        return cleaned
    
    def authenticate(self):
        """Google Sheets API 認證"""
        # 檢查是否有已存在的token
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # 如果沒有有效的憑證，則進行認證
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # 儲存憑證以供下次使用
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('sheets', 'v4', credentials=self.creds)
    
    def read_sheet_data(self, spreadsheet_id: str, range_name: str) -> List[List]:
        """讀取Google Sheets資料"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            return result.get('values', [])
        except Exception as e:
            print(f"讀取資料時發生錯誤: {e}")
            return []
    
    def update_sheet_data(self, spreadsheet_id: str, range_name: str, values: List[List]):
        """更新Google Sheets資料"""
        try:
            # 自動根據資料長度決定 range
            if values and len(values) == 1:
                row_data = values[0]
                row_idx = int(re.findall(r'(\d+)', range_name)[0])
                data_len = len(row_data)
                start_col = 'A'
                end_col = chr(ord('A') + data_len - 1)
                range_name = f"交易!{start_col}{row_idx}:{end_col}{row_idx}"
            else:
                # 添加分頁名稱
                if not range_name.startswith('交易!'):
                    range_name = f"交易!{range_name}"
            body = {
                'values': values
            }
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            print(f"已更新 {result.get('updatedCells')} 個儲存格")
            return True
        except Exception as e:
            print(f"更新資料時發生錯誤: {e}")
            return False
    
    def update_single_cell(self, spreadsheet_id: str, cell: str, value):
        """只更新單一 cell，不動其他欄位"""
        try:
            # 寫入到第二個分頁「交易」（從哪讀就寫到哪）
            cell_with_sheet = f"交易!{cell}"
            body = {'values': [[value]]}
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=cell_with_sheet,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            print(f"已更新 {cell_with_sheet} → {value}")
            return True
        except Exception as e:
            print(f"更新 {cell_with_sheet} 時發生錯誤: {e}")
            return False



    def fill_symbols_from_urls(self, spreadsheet_id: str, url_column: str, start_row: int = 2, end_row: Optional[int] = None):
        """第一步：只根據網址爬取資料，填寫 symbol 等欄位，不處理價格"""
        # 讀取第二個分頁（交易分頁）的第1行作為標題行
        header_range = "交易!1:1"
        headers = self.read_sheet_data(spreadsheet_id, header_range)
        if not headers or not headers[0]:
            print("無法讀取表頭")
            return
        header_row = headers[0]
        
        # 使用 config.py 中的欄位映射，確保絕對安全
        safe_field_mapping = config.COLUMN_MAPPINGS
        
        # 驗證欄位位置是否正確
        print("驗證欄位位置:")
        validation_passed = True
        for field, col_idx in safe_field_mapping.items():
            if col_idx < len(header_row):
                col_letter = chr(65 + col_idx)
                header = header_row[col_idx]
                print(f"  {col_letter}: {header} -> {field}")
                
                # 檢查欄位名稱是否合理
                if field == 'address' and 'address' not in header.lower():
                    print(f"    ⚠️  警告: {col_letter} 欄位名稱 '{header}' 可能不是 Address")
                    validation_passed = False
                elif field == 'symbol' and 'symbol' not in header.lower():
                    print(f"    ⚠️  警告: {col_letter} 欄位名稱 '{header}' 可能不是 Symbol")
                    validation_passed = False
            else:
                print(f"  ⚠️  警告: {field} 欄位索引 {col_idx} 超出範圍")
                validation_passed = False
        
        if not validation_passed:
            print("欄位驗證失敗，停止執行以避免覆蓋錯誤欄位")
            return
        
        # 讀取完整的資料範圍
        data_range = f"交易!A{start_row}:Z{end_row if end_row else ''}"
        all_data = self.read_sheet_data(spreadsheet_id, data_range)
        
        # 讀取URL欄位的資料
        url_range = f"交易!{url_column}{start_row}:{url_column}{end_row if end_row else ''}"
        url_data = self.read_sheet_data(spreadsheet_id, url_range)
        
        # 確保我們處理所有行，包括空行
        total_rows = end_row - start_row + 1 if end_row else len(all_data)
        print(f"總共需要處理 {total_rows} 行")
        
        # 批次更新，減少 API 呼叫
        batch_updates = []
        updated_count = 0
        
        for i, row in enumerate(url_data):
            if not row:
                # 處理空行，至少填入 last_updated
                print(f"\n處理第 {start_row + i} 行: 空行")
                row_updates = []
                for field, col_idx in safe_field_mapping.items():
                    if field == 'last_updated':
                        value = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                        col_letter = chr(65 + col_idx)
                        row_num = start_row + i
                        cell = f"{col_letter}{row_num}"
                        header = header_row[col_idx] if col_idx < len(header_row) else f"Column{col_idx}"
                        row_updates.append((cell, value))
                        print(f"  準備更新: {cell} ({header}) = {value}")
                
                if row_updates:
                    batch_updates.append(row_updates)
                    updated_count += 1
                    print(f"  加入批次更新: {len(row_updates)} 個欄位")
                continue
            
            url = row[0] if row else ''
            if not url:
                # 處理沒有URL的行，至少填入 last_updated
                print(f"\n處理第 {start_row + i} 行: 沒有URL")
                row_updates = []
                for field, col_idx in safe_field_mapping.items():
                    if field == 'last_updated':
                        value = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                        col_letter = chr(65 + col_idx)
                        row_num = start_row + i
                        cell = f"{col_letter}{row_num}"
                        header = header_row[col_idx] if col_idx < len(header_row) else f"Column{col_idx}"
                        row_updates.append((cell, value))
                        print(f"  準備更新: {cell} ({header}) = {value}")
                
                if row_updates:
                    batch_updates.append(row_updates)
                    updated_count += 1
                    print(f"  加入批次更新: {len(row_updates)} 個欄位")
                continue
                
            print(f"\n處理第 {start_row + i} 行: {url}")
            scraped_info = self.scrape_block_explorer_data(url)
            
            # 收集這一行要更新的所有欄位
            row_updates = []
            
            for field, col_idx in safe_field_mapping.items():
                value = scraped_info.get(field, '')
                # 對金額欄位進行清理
                if field in ['collateral_amount', 'balance', 'change', 'realized_pnl', 'unrealized_pnl']:
                    value = self.clean_monetary_value(value)
                if field == 'last_updated':
                    value = scraped_info.get('last_updated', '')
                
                col_letter = chr(65 + col_idx)
                row_num = start_row + i
                cell = f"{col_letter}{row_num}"
                header = header_row[col_idx] if col_idx < len(header_row) else f"Column{col_idx}"
                row_updates.append((cell, value))
                print(f"  準備更新: {cell} ({header}) = {value}")
            
            # 將這一行加入批次更新
            if row_updates:
                batch_updates.append(row_updates)
                updated_count += 1
                print(f"  加入批次更新: {len(row_updates)} 個欄位")
            else:
                print(f"  沒有需要更新的欄位")
            
            time.sleep(1)
        
        # 執行批次更新
        if batch_updates:
            print(f"\n執行批次更新: {len(batch_updates)} 行，共 {sum(len(row) for row in batch_updates)} 個儲存格")
            self._batch_update_cells(spreadsheet_id, batch_updates)
        
        print(f"成功處理 {updated_count} 行 symbol/基本資料填寫")
    
    def _batch_update_cells(self, spreadsheet_id: str, batch_updates: List[List[tuple]], max_retries: int = 3):
        """批次更新多個 cell，減少 API 呼叫次數，加入重試機制"""
        try:
            # 將所有更新合併成一個批次請求
            all_updates = []
            for row_updates in batch_updates:
                for cell, value in row_updates:
                    # 添加分頁名稱
                    cell_with_sheet = f"交易!{cell}"
                    all_updates.append({
                        'range': cell_with_sheet,
                        'values': [[value]]
                    })
            
            # 分批執行，每批最多 10 個更新
            batch_size = 10
            for i in range(0, len(all_updates), batch_size):
                batch = all_updates[i:i + batch_size]
                
                # 重試機制
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        body = {
                            'valueInputOption': 'USER_ENTERED',
                            'data': batch
                        }
                        
                        result = self.service.spreadsheets().values().batchUpdate(
                            spreadsheetId=spreadsheet_id,
                            body=body
                        ).execute()
                        
                        print(f"批次更新完成: {result.get('totalUpdatedCells', 0)} 個儲存格")
                        break  # 成功則跳出重試迴圈
                        
                    except Exception as e:
                        retry_count += 1
                        error_msg = str(e)
                        
                        if "429" in error_msg or "quota" in error_msg.lower():
                            # API配額限制，等待更長時間
                            wait_time = 30 * retry_count  # 30秒, 60秒, 90秒
                            print(f"API配額限制，等待 {wait_time} 秒後重試 ({retry_count}/{max_retries})")
                            time.sleep(wait_time)
                        elif "network" in error_msg.lower() or "timeout" in error_msg.lower():
                            # 網路錯誤，短暫等待
                            wait_time = 5 * retry_count  # 5秒, 10秒, 15秒
                            print(f"網路錯誤，等待 {wait_time} 秒後重試 ({retry_count}/{max_retries})")
                            time.sleep(wait_time)
                        else:
                            # 其他錯誤，短暫等待
                            wait_time = 3 * retry_count  # 3秒, 6秒, 9秒
                            print(f"更新錯誤: {error_msg}")
                            print(f"等待 {wait_time} 秒後重試 ({retry_count}/{max_retries})")
                            time.sleep(wait_time)
                        
                        if retry_count >= max_retries:
                            print(f"批次更新失敗，已重試 {max_retries} 次，跳過此批次")
                            # 嘗試單個更新作為最後手段
                            self._fallback_single_updates(spreadsheet_id, batch)
                            break
                
                # 批次間延遲，避免 429 錯誤
                if i + batch_size < len(all_updates):
                    time.sleep(2)
                    
        except Exception as e:
            print(f"批次更新時發生嚴重錯誤: {e}")
            print("嘗試單個更新作為備用方案...")
            # 如果批次更新完全失敗，嘗試單個更新
            self._fallback_single_updates(spreadsheet_id, batch_updates)

    def _fallback_single_updates(self, spreadsheet_id: str, batch_updates: List[List[tuple]]):
        """備用方案：單個儲存格更新"""
        print("使用單個更新備用方案...")
        success_count = 0
        total_count = 0
        
        for row_updates in batch_updates:
            for cell, value in row_updates:
                total_count += 1
                try:
                    self.update_single_cell(spreadsheet_id, cell, value)
                    success_count += 1
                    time.sleep(0.5)  # 單個更新間隔
                except Exception as e:
                    print(f"單個更新失敗 {cell}: {e}")
                    continue
        
        print(f"備用更新完成: {success_count}/{total_count} 個儲存格成功更新")

    def fill_prices_by_symbol(self, spreadsheet_id: str, start_row: int = 2, end_row: Optional[int] = None):
        """第二步：根據 symbol 欄位批次查價，填入 Price 欄位（支援兩組倉位）"""
        header_range = "交易!1:1"  # 讀取第二個分頁（交易分頁）的第1行作為標題行
        headers = self.read_sheet_data(spreadsheet_id, header_range)
        if not headers or not headers[0]:
            print("無法讀取表頭")
            return
        header_row = headers[0]
        
        # 使用 config.py 中的欄位位置
        symbol1_col = config.COLUMN_MAPPINGS['symbol']    # I欄
        price1_col = config.COLUMN_MAPPINGS['price']      # J欄
        symbol2_col = config.COLUMN_MAPPINGS['symbol2']   # P欄
        price2_col = config.COLUMN_MAPPINGS['price2']     # Q欄
        
        # 驗證欄位位置
        if (symbol1_col >= len(header_row) or price1_col >= len(header_row) or 
            symbol2_col >= len(header_row) or price2_col >= len(header_row)):
            print("欄位索引超出範圍，停止執行")
            return
        
        symbol1_header = header_row[symbol1_col]
        price1_header = header_row[price1_col]
        symbol2_header = header_row[symbol2_col]
        price2_header = header_row[price2_col]
        
        print(f"\n價格查詢設定:")
        print(f"  第一組倉位:")
        print(f"    Symbol1欄位: {chr(65 + symbol1_col)} ({symbol1_header})")
        print(f"    Price1欄位: {chr(65 + price1_col)} ({price1_header})")
        print(f"  第二組倉位:")
        print(f"    Symbol2欄位: {chr(65 + symbol2_col)} ({symbol2_header})")
        print(f"    Price2欄位: {chr(65 + price2_col)} ({price2_header})")
        
        # 驗證欄位名稱
        if 'symbol' not in symbol1_header.lower():
            print(f"⚠️  警告: {chr(65 + symbol1_col)} 欄位名稱 '{symbol1_header}' 可能不是 Symbol1")
            return
        
        if 'price' not in price1_header.lower():
            print(f"⚠️  警告: {chr(65 + price1_col)} 欄位名稱 '{price1_header}' 可能不是 Price1")
            return
        
        if 'symbol' not in symbol2_header.lower():
            print(f"⚠️  警告: {chr(65 + symbol2_col)} 欄位名稱 '{symbol2_header}' 可能不是 Symbol2")
            return
        
        if 'price' not in price2_header.lower():
            print(f"⚠️  警告: {chr(65 + price2_col)} 欄位名稱 '{price2_header}' 可能不是 Price2")
            return
        
        data_range = f"交易!A{start_row}:Z{end_row if end_row else ''}"
        all_data = self.read_sheet_data(spreadsheet_id, data_range)
        
        # 收集所有 symbol（第一組和第二組）
        symbol_set = set()
        symbol1_rows = {}  # 記錄每個symbol1對應的行號
        symbol2_rows = {}  # 記錄每個symbol2對應的行號
        
        for i, row in enumerate(all_data):
            # 處理第一組倉位
            if len(row) > symbol1_col and row[symbol1_col]:
                symbol = row[symbol1_col]
                # 去掉s前綴用於價格查詢
                clean_symbol = symbol.replace('s', '') if symbol.startswith('s') else symbol
                symbol_set.add(clean_symbol)
                if clean_symbol not in symbol1_rows:
                    symbol1_rows[clean_symbol] = []
                symbol1_rows[clean_symbol].append(i)
            
            # 處理第二組倉位
            if len(row) > symbol2_col and row[symbol2_col]:
                symbol = row[symbol2_col]
                # 去掉s前綴用於價格查詢
                clean_symbol = symbol.replace('s', '') if symbol.startswith('s') else symbol
                symbol_set.add(clean_symbol)
                if clean_symbol not in symbol2_rows:
                    symbol2_rows[clean_symbol] = []
                symbol2_rows[clean_symbol].append(i)
        
        print(f"\n找到的幣種: {list(symbol_set)}")
        print(f"第一組倉位:")
        for symbol, rows in symbol1_rows.items():
            print(f"  {symbol}: 第 {[start_row + r for r in rows]} 行")
        print(f"第二組倉位:")
        for symbol, rows in symbol2_rows.items():
            print(f"  {symbol}: 第 {[start_row + r for r in rows]} 行")
        
        # 批次查價
        print(f"\n開始批次查價...")
        prices = self.price_fetcher.get_prices_for_symbols(list(symbol_set))
        
        print(f"查價結果:")
        for symbol, price in prices.items():
            print(f"  {symbol}: ${price}")
        
        # 批次寫入價格
        price_updates = []
        updated_count = 0
        
        for i, row in enumerate(all_data):
            # 處理第一組倉位價格
            if len(row) > symbol1_col and row[symbol1_col]:
                symbol = row[symbol1_col]
                # 去掉s前綴用於價格查詢
                clean_symbol = symbol.replace('s', '') if symbol.startswith('s') else symbol
                price = prices.get(clean_symbol)
                if price is not None:
                    col_letter = chr(65 + price1_col)
                    row_num = start_row + i
                    cell = f"{col_letter}{row_num}"
                    value = self.clean_monetary_value(f"{price:.2f}")
                    price_updates.append((cell, value))
                    print(f"  準備更新第一組價格: {cell} ({price1_header}) = {value} ({clean_symbol})")
                    updated_count += 1
                else:
                    print(f"  跳過第一組價格更新: {clean_symbol} 沒有價格資料")
            
            # 處理第二組倉位價格
            if len(row) > symbol2_col and row[symbol2_col]:
                symbol = row[symbol2_col]
                # 去掉s前綴用於價格查詢
                clean_symbol = symbol.replace('s', '') if symbol.startswith('s') else symbol
                price = prices.get(clean_symbol)
                if price is not None:
                    col_letter = chr(65 + price2_col)
                    row_num = start_row + i
                    cell = f"{col_letter}{row_num}"
                    value = self.clean_monetary_value(f"{price:.2f}")
                    price_updates.append((cell, value))
                    print(f"  準備更新第二組價格: {cell} ({price2_header}) = {value} ({clean_symbol})")
                    updated_count += 1
                else:
                    print(f"  跳過第二組價格更新: {clean_symbol} 沒有價格資料")
        
        # 批次更新價格
        if price_updates:
            print(f"\n執行價格批次更新: {len(price_updates)} 個儲存格")
            self._batch_update_cells(spreadsheet_id, [price_updates])
        
        print(f"成功填入 {updated_count} 行價格")

    def scrape_block_explorer_data(self, url: str, max_retries: int = 3) -> Dict[str, str]:
        """爬取區塊瀏覽器網址的實際資料，加入重試機制"""
        if not url or pd.isna(url):
            return {}
        
        url = str(url).strip()
        
        for retry_count in range(max_retries):
            try:
                print(f"正在爬取: {url} (嘗試 {retry_count + 1}/{max_retries})")
                
                # 設定請求標頭，模擬瀏覽器
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                # 發送請求
                response = requests.get(url, headers=headers, timeout=15)  # 增加超時時間
                response.raise_for_status()
                
                # 解析HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                result = {
                    'address': '',
                    'collateral_amount': '',
                    'open_positions': '',
                    'balance': '',
                    'change': '',
                    'last_activity': '',
                    'last_updated': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                    # 第一組倉位
                    'symbol1': '',
                    'size1': '',
                    'direction1': '',
                    'realized_pnl1': '',
                    'unrealized_pnl1': '',
                    'price1': '',
                    # 第二組倉位
                    'symbol2': '',
                    'size2': '',
                    'direction2': '',
                    'realized_pnl2': '',
                    'unrealized_pnl2': '',
                    'price2': '',
                    # 保持向後相容的欄位
                    'symbol': '',
                    'size': '',
                    'direction': '',
                    'realized_pnl': '',
                    'unrealized_pnl': '',
                    'current_price': ''  # 保留原有價格欄位
                }
                
                # 尋找地址（通常是以0x開頭的長字串）
                addresses = soup.find_all(string=lambda text: text and len(text) > 20 and text.startswith('0x'))
                if addresses:
                    result['address'] = addresses[0].strip()
                
                # 尋找金額資料（包含$符號的數字）
                money_patterns = soup.find_all(string=lambda text: text and '$' in text and any(char.isdigit() for char in text))
                for pattern in money_patterns:
                    text = pattern.strip()
                    if '$' in text and any(char.isdigit() for char in text):
                        # 第一個金額通常是餘額
                        if not result['balance']:
                            result['balance'] = self.clean_monetary_value(text)
                        # 第二個金額通常是變化
                        elif not result['change']:
                            result['change'] = self.clean_monetary_value(text)
                
                # 尋找Collateral Amount - 使用更簡單的方法
                # 從所有文字中尋找包含"Collateral Amount:"的行
                all_text = soup.get_text()
                lines = all_text.split('\n')
                for line in lines:
                    if 'Collateral Amount:' in line and '$' in line:
                        # 提取金額
                        dollar_index = line.find('$')
                        if dollar_index != -1:
                            # 找到$後的下一個空格或行尾
                            end_index = line.find(' ', dollar_index)
                            if end_index == -1:
                                end_index = len(line)
                            collateral_amount = line[dollar_index:end_index].strip()
                            # 清理可能的額外文字
                            if 'Open' in collateral_amount:
                                collateral_amount = collateral_amount.replace('Open', '').strip()
                            # 去掉 $ 符號（更強力的清理）
                            collateral_amount = collateral_amount.replace('$', '').replace('＄', '').strip()
                            # 確保沒有其他貨幣符號
                            collateral_amount = re.sub(r'[^\d\-\.]', '', collateral_amount)
                            result['collateral_amount'] = self.clean_monetary_value(collateral_amount)
                            break
                
                # 尋找Open Positions - 支援兩組倉位
                open_positions = []
                position_count = 0
                
                # 由於頁面內容可能被壓縮在一行中，使用正則表達式來匹配倉位模式
                all_text = soup.get_text()
                
                # 使用正則表達式來匹配倉位模式 - 支援多種格式
                position_patterns = [
                    # 原始格式：LDO Size: 62.0 Side: SHORT
                    r'([A-Z]{2,10})Size:\s*([\d\.]+)\s*Side:\s*(SHORT|LONG)\s*Realized PnL:\s*([$\-\d,\.]+)\s*Unrealized PnL:\s*([$\-\d,\.]+)',
                    # AI16Z格式：AI16ZSize: 3265.3 Side: SHORT
                    r'([A-Z0-9]{2,10})Size:\s*([\d\.]+)\s*Side:\s*(SHORT|LONG)\s*Realized PnL:\s*([$\-\d,\.]+)\s*Unrealized PnL:\s*([$\-\d,\.]+)',
                    # 簡化格式：Size: 3265.3 Side: SHORT
                    r'Size:\s*([\d\.]+)\s*Side:\s*(SHORT|LONG)\s*Realized PnL:\s*([$\-\d,\.]+)\s*Unrealized PnL:\s*([$\-\d,\.]+)',
                ]
                
                matches = []
                for pattern in position_patterns:
                    matches = re.findall(pattern, all_text)
                    if matches:
                        print(f"使用模式找到 {len(matches)} 個倉位匹配: {pattern}")
                        break
                
                print(f"找到 {len(matches)} 個倉位匹配")
                
                for i, match in enumerate(matches[:2]):  # 只處理前兩個倉位
                    position_count += 1
                    
                    # 處理不同格式的匹配結果
                    if len(match) == 5:  # 完整格式：包含幣種代碼
                        symbol, size, side, realized_pnl, unrealized_pnl = match
                    elif len(match) == 4:  # 簡化格式：沒有幣種代碼
                        size, side, realized_pnl, unrealized_pnl = match
                        symbol = 'AI16Z'  # 預設幣種代碼
                    else:
                        continue
                    
                    # 清理PnL值
                    realized_pnl_clean = self.clean_monetary_value(realized_pnl)
                    unrealized_pnl_clean = self.clean_monetary_value(unrealized_pnl)
                    
                    # 去掉s前綴用於顯示
                    clean_symbol = symbol.replace('s', '') if symbol.startswith('s') else symbol
                    
                    # 組合倉位資訊
                    position_info = f"{clean_symbol} | Size: {size} | Side: {side}"
                    if realized_pnl_clean:
                        position_info += f" | Realized PnL: {realized_pnl_clean}"
                    if unrealized_pnl_clean:
                        position_info += f" | Unrealized PnL: {unrealized_pnl_clean}"
                    
                    open_positions.append(position_info)
                    
                    # 設定對應組別的詳細資訊
                    if position_count == 1:
                        # 第一組倉位
                        result['symbol1'] = clean_symbol
                        result['size1'] = size
                        result['direction1'] = side
                        result['realized_pnl1'] = realized_pnl_clean
                        result['unrealized_pnl1'] = unrealized_pnl_clean
                        
                        # 設定第一個倉位為主要倉位（保持向後相容）
                        if not result['symbol']:
                            result['symbol'] = clean_symbol
                            result['size'] = size
                            result['direction'] = side
                            result['realized_pnl'] = realized_pnl_clean
                            result['unrealized_pnl'] = unrealized_pnl_clean
                            
                    elif position_count == 2:
                        # 第二組倉位
                        result['symbol2'] = clean_symbol
                        result['size2'] = size
                        result['direction2'] = side
                        result['realized_pnl2'] = realized_pnl_clean
                        result['unrealized_pnl2'] = unrealized_pnl_clean
                
                # 組合倉位資訊 - 分別填入 Open Positions1 和 Open Positions2
                if len(open_positions) >= 1:
                    result['open_positions'] = open_positions[0]  # 第一組倉位
                if len(open_positions) >= 2:
                    result['open_positions2'] = open_positions[1]  # 第二組倉位
                
                print(f"成功爬取資料: {url}")
                return result
                
            except requests.exceptions.RequestException as e:
                print(f"網路錯誤 (嘗試 {retry_count + 1}/{max_retries}): {e}")
                if retry_count < max_retries - 1:
                    wait_time = 5 * (retry_count + 1)  # 5秒, 10秒, 15秒
                    print(f"等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                else:
                    print(f"爬取失敗，已重試 {max_retries} 次: {url}")
                    return {}
                    
            except Exception as e:
                print(f"爬取錯誤 (嘗試 {retry_count + 1}/{max_retries}): {e}")
                if retry_count < max_retries - 1:
                    wait_time = 3 * (retry_count + 1)  # 3秒, 6秒, 9秒
                    print(f"等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                else:
                    print(f"爬取失敗，已重試 {max_retries} 次: {url}")
                    return {}
        
        return {}

# main 流程
if __name__ == "__main__":
    import schedule
    import time
    from datetime import datetime
    
    from config import SPREADSHEET_ID, URL_COLUMN, START_ROW, END_ROW
    
    def run_main_process():
        """執行主要處理流程，加入完整的錯誤處理"""
        print(f"\n{'='*50}")
        print(f"開始執行 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        processor = None
        try:
            processor = SheetsProcessor()
            print("正在進行Google Sheets認證...")
            processor.authenticate()
            print("認證成功！")
            
        except Exception as e:
            print(f"認證失敗: {e}")
            print("請檢查 credentials.json 檔案和網路連線")
            print(f"{'='*50}\n")
            return
        
        # 步驟1：填寫 symbol/基本資料
        try:
            print("=== 步驟1：填寫 symbol/基本資料 ===")
            processor.fill_symbols_from_urls(SPREADSHEET_ID, URL_COLUMN, START_ROW, END_ROW)
            print("步驟1完成")
        except Exception as e:
            print(f"步驟1失敗: {e}")
            print("繼續執行步驟2...")
        
        # 步驟2：根據 symbol 批次查價並填入 Price
        try:
            print("=== 步驟2：根據 symbol 批次查價並填入 Price ===")
            processor.fill_prices_by_symbol(SPREADSHEET_ID, START_ROW, END_ROW)
            print("步驟2完成")
        except Exception as e:
            print(f"步驟2失敗: {e}")
            print("價格更新跳過，其他資料已更新")
        
        print("全部完成！")
        print(f"執行完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
    
    # 設定排程：每個整點執行
    schedule.every().hour.at(":00").do(run_main_process)
    
    print("=" * 60)
    print("    Google Sheets 自動處理程式")
    print("=" * 60)
    print(f"啟動時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("排程設定: 每個整點自動執行")
    print("按 Ctrl+C 停止程式")
    print("=" * 60)
    
    # 啟動時立即執行一次
    print("\n立即執行第一次...")
    run_main_process()
    
    print("排程器已啟動，等待下次執行...")
    print("下次執行時間:", schedule.next_run())
    
    try:
        # 持續運行排程器
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分鐘檢查一次
            
    except KeyboardInterrupt:
        print("\n程式已停止") 