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
                range_name = f"{start_col}{row_idx}:{end_col}{row_idx}"
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
            body = {'values': [[value]]}
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=cell,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            print(f"已更新 {cell} → {value}")
            return True
        except Exception as e:
            print(f"更新 {cell} 時發生錯誤: {e}")
            return False



    def fill_symbols_from_urls(self, spreadsheet_id: str, url_column: str, start_row: int = 2, end_row: Optional[int] = None):
        """第一步：只根據網址爬取資料，填寫 symbol 等欄位，不處理價格"""
        header_range = "1:1"
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
        
        url_range = f"{url_column}{start_row}:{url_column}{end_row if end_row else ''}"
        url_data = self.read_sheet_data(spreadsheet_id, url_range)
        data_range = f"A{start_row}:Z{end_row if end_row else ''}"
        all_data = self.read_sheet_data(spreadsheet_id, data_range)
        
        # 批次更新，減少 API 呼叫
        batch_updates = []
        updated_count = 0
        
        for i, row in enumerate(url_data):
            if not row:
                continue
            url = row[0] if row else ''
            if not url:
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
                header = header_row[col_idx]
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
                    all_updates.append({
                        'range': cell,
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
        """第二步：根據 symbol 欄位批次查價，填入 Price 欄位"""
        header_range = "1:1"
        headers = self.read_sheet_data(spreadsheet_id, header_range)
        if not headers or not headers[0]:
            print("無法讀取表頭")
            return
        header_row = headers[0]
        
        # 使用 config.py 中的欄位位置
        symbol_col = config.COLUMN_MAPPINGS['symbol']   # I欄
        price_col = config.COLUMN_MAPPINGS['price']     # J欄
        
        # 驗證欄位位置
        if symbol_col >= len(header_row) or price_col >= len(header_row):
            print("欄位索引超出範圍，停止執行")
            return
        
        symbol_header = header_row[symbol_col]
        price_header = header_row[price_col]
        
        print(f"\n價格查詢設定:")
        print(f"  Symbol欄位: {chr(65 + symbol_col)} ({symbol_header})")
        print(f"  Price欄位: {chr(65 + price_col)} ({price_header})")
        
        # 驗證欄位名稱
        if 'symbol' not in symbol_header.lower():
            print(f"⚠️  警告: {chr(65 + symbol_col)} 欄位名稱 '{symbol_header}' 可能不是 Symbol")
            return
        
        if 'price' not in price_header.lower():
            print(f"⚠️  警告: {chr(65 + price_col)} 欄位名稱 '{price_header}' 可能不是 Price")
            return
        
        data_range = f"A{start_row}:Z{end_row if end_row else ''}"
        all_data = self.read_sheet_data(spreadsheet_id, data_range)
        
        # 收集所有 symbol
        symbol_set = set()
        symbol_rows = {}  # 記錄每個symbol對應的行號
        
        for i, row in enumerate(all_data):
            if len(row) > symbol_col and row[symbol_col]:
                symbol = row[symbol_col]
                # 去掉s前綴用於價格查詢
                clean_symbol = symbol.replace('s', '') if symbol.startswith('s') else symbol
                symbol_set.add(clean_symbol)
                if clean_symbol not in symbol_rows:
                    symbol_rows[clean_symbol] = []
                symbol_rows[clean_symbol].append(i)
        
        print(f"\n找到的幣種: {list(symbol_set)}")
        for symbol, rows in symbol_rows.items():
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
            if len(row) > symbol_col and row[symbol_col]:
                symbol = row[symbol_col]
                # 去掉s前綴用於價格查詢
                clean_symbol = symbol.replace('s', '') if symbol.startswith('s') else symbol
                price = prices.get(clean_symbol)
                if price is not None:
                    col_letter = chr(65 + price_col)
                    row_num = start_row + i
                    cell = f"{col_letter}{row_num}"
                    value = self.clean_monetary_value(f"{price:.2f}")
                    price_updates.append((cell, value))
                    print(f"  準備更新價格: {cell} ({price_header}) = {value} ({clean_symbol})")
                    updated_count += 1
                else:
                    print(f"  跳過價格更新: {clean_symbol} 沒有價格資料")
        
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
                    'symbol': '',
                    'size': '',
                    'direction': '',
                    'realized_pnl': '',
                    'unrealized_pnl': '',
                    'current_price': ''  # 新增價格欄位
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
                        # 第三個金額可能是抵押金額（先不設定，讓後面的專門處理）
                        # elif not result['collateral_amount']:
                        #     result['collateral_amount'] = text
                
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
                
                # 尋找Open Positions - 只顯示倉位資訊
                open_positions = []
                for idx, line in enumerate(lines):
                    if ('Size:' in line and 'Side:' in line):
                        # 幣種判斷 - 幣種通常直接跟在Open Positions後面
                        symbol = ''
                        
                        # 方法1: 在包含Size:的行中尋找幣種
                        # 幣種通常在"Open Positions"後面，Size:前面
                        if 'Open Positions' in line:
                            open_pos_start = line.find('Open Positions') + 13  # "Open Positions"長度
                            size_start = line.find('Size:')
                            if size_start > open_pos_start:
                                symbol_part = line[open_pos_start:size_start].strip()
                                # 清理可能的空格和特殊字符
                                symbol = symbol_part.split()[0] if symbol_part.split() else ''
                        
                        # 方法2: 如果方法1沒找到，嘗試從Size:前面找
                        if not symbol:
                            size_start = line.find('Size:')
                            if size_start > 0:
                                before_size = line[:size_start].strip()
                                # 找最後一個單詞作為幣種
                                words = before_size.split()
                                if words:
                                    potential_symbol = words[-1]
                                    # 排除明顯不是幣種的詞
                                    if potential_symbol.lower() not in ['positions', 'open', 'zklighter']:
                                        symbol = potential_symbol
                        
                        # 只處理有幣種的倉位
                        if symbol:
                            size = ''
                            size_start = line.find('Size:') + 5
                            size_end = line.find('Side:')
                            if size_start != -1 and size_end != -1:
                                size = line[size_start:size_end].strip()
                            
                            side = ''
                            side_start = line.find('Side:') + 5
                            side_end = line.find('Realized PnL:')
                            if side_end == -1:
                                side_end = len(line)
                            side = line[side_start:side_end].strip()
                            
                            # 提取PnL（只保留金額）
                            realized_pnl = ''
                            unrealized_pnl = ''
                            
                            # 尋找Realized PnL - 使用正則表達式
                            realized_match = re.search(r'Realized PnL:\s*([$\-\d,\.]+)', line)
                            if realized_match:
                                realized_text = realized_match.group(1)
                                # 清理可能的額外文字
                                realized_text = re.sub(r'[^\d\-\.]', '', realized_text)
                                realized_pnl = self.clean_monetary_value(realized_text)
                            
                            # 尋找Unrealized PnL - 使用正則表達式
                            unrealized_match = re.search(r'Unrealized PnL:\s*([$\-\d,\.]+)', line)
                            if unrealized_match:
                                unrealized_text = unrealized_match.group(1)
                                # 清理可能的額外文字
                                unrealized_text = re.sub(r'[^\d\-\.]', '', unrealized_text)
                                unrealized_pnl = self.clean_monetary_value(unrealized_text)
                            
                            # 組合倉位資訊
                            # 去掉s前綴用於顯示
                            clean_symbol = symbol.replace('s', '') if symbol.startswith('s') else symbol
                            position_info = f"{clean_symbol} | Size: {size} | Side: {side}"
                            if realized_pnl:
                                position_info += f" | Realized PnL: {realized_pnl}"
                            if unrealized_pnl:
                                position_info += f" | Unrealized PnL: {unrealized_pnl}"
                            
                            open_positions.append(position_info)
                            
                            # 設定第一個倉位的詳細資訊
                            if not result['symbol']:
                                # 去掉s前綴
                                clean_symbol = symbol.replace('s', '') if symbol.startswith('s') else symbol
                                result['symbol'] = clean_symbol
                                result['size'] = size
                                result['direction'] = side
                                result['realized_pnl'] = realized_pnl
                                result['unrealized_pnl'] = unrealized_pnl
                
                # 組合所有倉位資訊
                if open_positions:
                    result['open_positions'] = ' | '.join(open_positions)
                
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