import requests
from datetime import datetime

class KrakenLedger:
    def __init__(self, api):
        self.__api = api

    def get_price(self, pair, timestamp):
        url = f"https://api.kraken.com/0/public/OHLC?pair={pair}&interval=1440&since={int(timestamp)}"
        try:
            resp = requests.get(url).json()
            result_key = list(resp["result"].keys())[0]
            ohlc_data = resp["result"][result_key]
            if not ohlc_data:
                return None
            return float(ohlc_data[0][4])
        except Exception as e:
            print(f"Error fetching price for {pair} at {datetime.utcfromtimestamp(timestamp)}: {e}")
            print(url)
            return None

    def fetch_history(self, ledger_type, offset):
        if ledger_type == 'staking':
            result = self.__api.kraken_api_call('/0/private/Ledgers', {'type': ledger_type, 'ofs': offset})
            ledger = 'ledger'
        elif ledger_type == 'trading':
            result = self.__api.kraken_api_call('/0/private/TradesHistory', {'ofs': offset})
            ledger = 'trades'
        else:
            result = {}
            ledger = None
        return ledger, result