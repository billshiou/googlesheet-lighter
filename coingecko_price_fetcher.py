import requests
import time
from typing import Dict, List, Optional
import json

class CoinGeckoPriceFetcher:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        
        # 常見幣種的 symbol 到 CoinGecko ID 對照表
        self.symbol_to_id = {
            'AVAX': 'avalanche-2',
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'USDC': 'usd-coin',
            'USDT': 'tether',
            'SOL': 'solana',
            'MATIC': 'matic-network',
            'LINK': 'chainlink',
            'UNI': 'uniswap',
            'AAVE': 'aave',
            'CRV': 'curve-dao-token',
            'COMP': 'compound-governance-token',
            'MKR': 'maker',
            'SNX': 'havven',
            'YFI': 'yearn-finance',
            'SUSHI': 'sushi',
            '1INCH': '1inch',
            'BAL': 'balancer',
            'REN': 'republic-protocol',
            'KNC': 'kyber-network-crystal',
            'ZRX': '0x',
            'BAND': 'band-protocol',
            'UMA': 'uma',
            'BADGER': 'badger-dao',
            'ALPHA': 'alpha-finance-lab',
            'PERP': 'perpetual-protocol',
            'RARI': 'rarible',
            'MASK': 'mask-network',
            'ENS': 'ethereum-name-service',
            'OP': 'optimism',
            'ARB': 'arbitrum',
            'PEPE': 'pepe',
            'SHIB': 'shiba-inu',
            'DOGE': 'dogecoin',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'LTC': 'litecoin',
            'BCH': 'bitcoin-cash',
            'XRP': 'ripple',
            'TRX': 'tron',
            'EOS': 'eos',
            'XLM': 'stellar',
            'VET': 'vechain',
            'THETA': 'theta-token',
            'FIL': 'filecoin',
            'ICP': 'internet-computer',
            'NEAR': 'near',
            'FTM': 'fantom',
            'ALGO': 'algorand',
            'ATOM': 'cosmos',
            'XTZ': 'tezos',
            'DASH': 'dash',
            'ZEC': 'zcash',
            'XMR': 'monero',
            'NEO': 'neo',
            'IOTA': 'iota',
            'WAVES': 'waves',
            'HBAR': 'hedera-hashgraph',
            'MANA': 'decentraland',
            'SAND': 'the-sandbox',
            'AXS': 'axie-infinity',
            'CHZ': 'chiliz',
            'HOT': 'holochain',
            'ENJ': 'enjincoin',
            'GALA': 'gala',
            'ROSE': 'oasis-network',
            'ONE': 'harmony',
            'IOTX': 'iotex',
            'ANKR': 'ankr',
            'COTI': 'coti',
            'OCEAN': 'ocean-protocol',
            'DYDX': 'dydx',
            'IMX': 'immutable-x',
            'GODS': 'gods-unchained',
            'ILV': 'illuvium',
            'RNDR': 'render-token',
            'HIVE': 'hive',
            'STEEM': 'steem',
            'HBD': 'hive-dollar',
            'TON': 'the-open-network',
            'POPCAT': 'popcat',
            'KAITO': 'kaito',
            # 新增一些常見的熱門幣種
            'BNB': 'binancecoin',
            'BUSD': 'binance-usd',
            'DAI': 'dai',
            'WBTC': 'wrapped-bitcoin',
            'WETH': 'weth',
            'CAKE': 'pancakeswap-token',
            'APT': 'aptos',
            'SUI': 'sui',
            'INJ': 'injective-protocol',
            'TIA': 'celestia',
            'PYTH': 'pyth-network',
            'JUP': 'jupiter',
            'BONK': 'bonk',
            'WIF': 'dogwifhat',
            'FLOKI': 'floki',
            'BOOK': 'book-of-meme',
            'MYRO': 'myro',
        }
        
        # 反向對照表：ID 到 symbol
        self.id_to_symbol = {v: k for k, v in self.symbol_to_id.items()}
        
        # 嘗試載入之前保存的對照表
        try:
            self.load_mapping()
        except:
            pass
    
    def get_symbol_id(self, symbol: str) -> Optional[str]:
        """根據 symbol 取得 CoinGecko ID"""
        return self.symbol_to_id.get(symbol.upper())
    
    def get_symbol_from_id(self, coin_id: str) -> Optional[str]:
        """根據 CoinGecko ID 取得 symbol"""
        return self.id_to_symbol.get(coin_id)
    
    def search_coin(self, query: str) -> List[Dict]:
        """搜尋幣種，回傳可能的匹配結果"""
        try:
            url = f"{self.base_url}/search"
            params = {"query": query}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('coins', [])
        except Exception as e:
            print(f"搜尋 {query} 時發生錯誤: {e}")
            return []
    
    def get_single_price(self, symbol: str, currency: str = 'usd', max_retries: int = 3) -> Optional[float]:
        """查詢單一幣種價格，加入重試機制"""
        if not symbol or not symbol.strip():
            return None
            
        symbol = symbol.strip().upper()
        coin_id = self.get_symbol_id(symbol)
        
        # 如果找不到對照，嘗試簡單搜尋
        if not coin_id:
            print(f"找不到 {symbol} 的 CoinGecko ID，嘗試搜尋...")
            coin_id = self._simple_search_coin_id(symbol)
            if coin_id:
                # 自動加入對照表
                self.add_custom_symbol(symbol, coin_id)
                print(f"已自動新增 {symbol} -> {coin_id} 到對照表")
        
        if not coin_id:
            print(f"無法找到 {symbol} 的 CoinGecko ID")
            return None
        
        for retry_count in range(max_retries):
            try:
                url = f"{self.base_url}/simple/price"
                params = {
                    "ids": coin_id,
                    "vs_currencies": currency
                }
                
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                if coin_id in data and currency in data[coin_id]:
                    return float(data[coin_id][currency])
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    wait_time = 30 * (retry_count + 1)  # 30秒, 60秒, 90秒
                    print(f"API配額限制，等待 {wait_time} 秒後重試 ({retry_count + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"HTTP錯誤 (嘗試 {retry_count + 1}/{max_retries}): {e}")
                    if retry_count < max_retries - 1:
                        time.sleep(5 * (retry_count + 1))
                    else:
                        break
                        
            except requests.exceptions.RequestException as e:
                print(f"網路錯誤 (嘗試 {retry_count + 1}/{max_retries}): {e}")
                if retry_count < max_retries - 1:
                    wait_time = 5 * (retry_count + 1)  # 5秒, 10秒, 15秒
                    print(f"等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                else:
                    break
                    
            except Exception as e:
                print(f"查詢 {symbol} 價格時發生錯誤 (嘗試 {retry_count + 1}/{max_retries}): {e}")
                if retry_count < max_retries - 1:
                    time.sleep(3 * (retry_count + 1))
                else:
                    break
        
        return None
    
    def _simple_search_coin_id(self, symbol: str) -> Optional[str]:
        """簡單搜尋幣種 ID"""
        try:
            results = self.search_coin(symbol)
            if results:
                # 優先選擇完全匹配的結果
                for result in results:
                    if result['symbol'].upper() == symbol.upper():
                        coin_id = result['id']
                        print(f"搜尋到完全匹配: {symbol} -> {coin_id} ({result['name']})")
                        return coin_id
                
                # 如果沒有完全匹配，取第一個結果
                coin_id = results[0]['id']
                print(f"搜尋到部分匹配: {symbol} -> {coin_id} ({results[0]['name']})")
                return coin_id
        except Exception as e:
            print(f"搜尋 {symbol} 時發生錯誤: {e}")
        
        return None
    
    def get_batch_prices(self, symbols: List[str], currency: str = 'usd') -> Dict[str, float]:
        """批次查詢多個幣種價格，使用智能搜尋"""
        if not symbols:
            return {}
        
        # 過濾出有效的 symbol 並取得對應的 ID
        valid_symbols = []
        coin_ids = []
        
        for symbol in symbols:
            if symbol and symbol.strip():
                symbol_clean = symbol.strip().upper()
                coin_id = self.get_symbol_id(symbol_clean)
                
                # 如果找不到對照，嘗試智能搜尋
                if not coin_id:
                    print(f"找不到 {symbol_clean} 的 CoinGecko ID，嘗試智能搜尋...")
                    coin_id = self._simple_search_coin_id(symbol_clean)
                    if coin_id:
                        # 自動加入對照表
                        self.add_custom_symbol(symbol_clean, coin_id)
                        print(f"已自動新增 {symbol_clean} -> {coin_id} 到對照表")
                
                if coin_id:
                    valid_symbols.append(symbol_clean)
                    coin_ids.append(coin_id)
                else:
                    print(f"警告: 無法找到 {symbol_clean} 的 CoinGecko ID")
        
        if not coin_ids:
            print("沒有有效的幣種可以查詢")
            return {}
        
        try:
            # 批次查詢
            url = f"{self.base_url}/simple/price"
            params = {
                "ids": ",".join(coin_ids),
                "vs_currencies": currency
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # 將結果轉換回 symbol -> price 的格式
            prices = {}
            for symbol, coin_id in zip(valid_symbols, coin_ids):
                if coin_id in data and currency in data[coin_id]:
                    prices[symbol] = float(data[coin_id][currency])
                    print(f"✓ {symbol}: ${prices[symbol]}")
                else:
                    print(f"✗ {symbol}: 無法取得價格")
            
            return prices
            
        except Exception as e:
            print(f"批次查詢價格時發生錯誤: {e}")
            return {}
    
    def get_batch_prices_with_delay(self, symbols: List[str], currency: str = 'usd', delay: float = 3.0, max_retries: int = 3) -> Dict[str, float]:
        """批次查詢多個幣種價格，加入重試機制、延遲和智能搜尋"""
        if not symbols:
            return {}
        
        # 過濾出有效的 symbol 並取得對應的 ID
        valid_symbols = []
        coin_ids = []
        
        for symbol in symbols:
            if symbol and symbol.strip():
                symbol_clean = symbol.strip().upper()
                coin_id = self.get_symbol_id(symbol_clean)
                
                # 如果找不到對照，嘗試智能搜尋
                if not coin_id:
                    print(f"找不到 {symbol_clean} 的 CoinGecko ID，嘗試智能搜尋...")
                    coin_id = self._simple_search_coin_id(symbol_clean)
                    if coin_id:
                        # 自動加入對照表
                        self.add_custom_symbol(symbol_clean, coin_id)
                        print(f"已自動新增 {symbol_clean} -> {coin_id} 到對照表")
                
                if coin_id:
                    valid_symbols.append(symbol_clean)
                    coin_ids.append(coin_id)
                else:
                    print(f"警告: 無法找到 {symbol_clean} 的 CoinGecko ID")
        
        if not coin_ids:
            print("沒有有效的幣種可以查詢")
            return {}
        
        results = {}
        
        # 分批處理，每批最多 50 個幣種
        batch_size = 50
        for i in range(0, len(coin_ids), batch_size):
            batch_ids = coin_ids[i:i + batch_size]
            batch_symbols = valid_symbols[i:i + batch_size]
            
            for retry_count in range(max_retries):
                try:
                    # 批次查詢
                    url = f"{self.base_url}/simple/price"
                    params = {
                        "ids": ",".join(batch_ids),
                        "vs_currencies": currency
                    }
                    
                    response = requests.get(url, params=params, timeout=20)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # 處理結果
                    for symbol, coin_id in zip(batch_symbols, batch_ids):
                        if coin_id in data and currency in data[coin_id]:
                            results[symbol] = float(data[coin_id][currency])
                        else:
                            print(f"警告: {symbol} 沒有價格資料")
                    
                    print(f"批次查詢成功: {len(batch_symbols)} 個幣種")
                    break  # 成功則跳出重試迴圈
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:  # Rate limit
                        wait_time = 60 * (retry_count + 1)  # 60秒, 120秒, 180秒
                        print(f"API配額限制，等待 {wait_time} 秒後重試 ({retry_count + 1}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        print(f"HTTP錯誤 (嘗試 {retry_count + 1}/{max_retries}): {e}")
                        if retry_count < max_retries - 1:
                            time.sleep(10 * (retry_count + 1))
                        else:
                            print(f"批次查詢失敗，嘗試單個查詢...")
                            # 如果批次查詢失敗，嘗試單個查詢
                            for symbol in batch_symbols:
                                price = self.get_single_price(symbol, currency, max_retries=2)
                                if price is not None:
                                    results[symbol] = price
                            break
                            
                except requests.exceptions.RequestException as e:
                    print(f"網路錯誤 (嘗試 {retry_count + 1}/{max_retries}): {e}")
                    if retry_count < max_retries - 1:
                        wait_time = 10 * (retry_count + 1)  # 10秒, 20秒, 30秒
                        print(f"等待 {wait_time} 秒後重試...")
                        time.sleep(wait_time)
                    else:
                        print(f"批次查詢失敗，嘗試單個查詢...")
                        # 如果批次查詢失敗，嘗試單個查詢
                        for symbol in batch_symbols:
                            price = self.get_single_price(symbol, currency, max_retries=2)
                            if price is not None:
                                results[symbol] = price
                        break
                        
                except Exception as e:
                    print(f"批次查詢時發生錯誤 (嘗試 {retry_count + 1}/{max_retries}): {e}")
                    if retry_count < max_retries - 1:
                        time.sleep(5 * (retry_count + 1))
                    else:
                        print(f"批次查詢失敗，嘗試單個查詢...")
                        # 如果批次查詢失敗，嘗試單個查詢
                        for symbol in batch_symbols:
                            price = self.get_single_price(symbol, currency, max_retries=2)
                            if price is not None:
                                results[symbol] = price
                        break
            
            # 批次間延遲
            if i + batch_size < len(coin_ids):
                print(f"等待 {delay} 秒後處理下一批...")
                time.sleep(delay)
        
        print(f"價格查詢完成: {len(results)}/{len(symbols)} 個幣種成功")
        return results
    
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """取得幣種的詳細市場資料"""
        coin_id = self.get_symbol_id(symbol)
        if not coin_id:
            print(f"找不到 {symbol} 的 CoinGecko ID")
            return None
        
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false",
                "sparkline": "false"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"取得 {symbol} 市場資料時發生錯誤: {e}")
            return None
    
    def get_trending_coins(self) -> List[Dict]:
        """取得趨勢幣種列表"""
        try:
            url = f"{self.base_url}/search/trending"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('coins', [])
            
        except Exception as e:
            print(f"取得趨勢幣種時發生錯誤: {e}")
            return []
    
    def add_custom_symbol(self, symbol: str, coin_id: str):
        """新增自定義的 symbol 對照"""
        self.symbol_to_id[symbol.upper()] = coin_id
        self.id_to_symbol[coin_id] = symbol.upper()
        print(f"已新增 {symbol} -> {coin_id} 的對照")
        # 自動保存到檔案
        self.save_mapping()
    
    def save_mapping(self, filename: str = "coin_mapping.json"):
        """儲存對照表到檔案"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.symbol_to_id, f, indent=2, ensure_ascii=False)
            print(f"對照表已儲存到 {filename}")
        except Exception as e:
            print(f"儲存對照表時發生錯誤: {e}")
    
    def load_mapping(self, filename: str = "coin_mapping.json"):
        """從檔案載入對照表"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.symbol_to_id.update(data)
                self.id_to_symbol = {v: k for k, v in self.symbol_to_id.items()}
            print(f"已從 {filename} 載入對照表")
        except Exception as e:
            print(f"載入對照表時發生錯誤: {e}")

# 使用範例
if __name__ == "__main__":
    fetcher = CoinGeckoPriceFetcher()
    
    print("=== 測試單一幣種查詢 ===")
    price = fetcher.get_single_price("AVAX")
    print(f"AVAX 價格: ${price}")
    
    print("\n=== 測試批次查詢 ===")
    symbols = ["BTC", "ETH", "SOL", "MATIC", "LINK"]
    prices = fetcher.get_batch_prices(symbols)
    print(f"批次查詢結果: {prices}")
    
    print("\n=== 測試搜尋功能 ===")
    results = fetcher.search_coin("avax")
    if results:
        print(f"搜尋 'avax' 結果: {results[0]['name']} ({results[0]['symbol'].upper()})")
    
    print("\n=== 測試趨勢幣種 ===")
    trending = fetcher.get_trending_coins()
    if trending:
        print(f"趨勢幣種: {trending[0]['item']['name']} ({trending[0]['item']['symbol'].upper()})") 