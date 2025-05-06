from source.utils import unique
import requests

ASSET_PAIR_CACHE_FILE = "asset_pair_cache.json"

import json
import os

class AssetPairs:
    def __init__(self, directory):
        self.__dir = directory
        self.__cache = {}

    def __get_cache_file_path(self):
        os.makedirs(self.__dir, exist_ok=True)
        return os.path.join(self.__dir, ASSET_PAIR_CACHE_FILE)

    def load_asset_pair_cache(self):
        file_path = self.__get_cache_file_path()
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                self.__cache = json.load(f)

    def save_asset_pair_cache(self):
        file_path = self.__get_cache_file_path()
        with open(file_path, "w") as f:
            json.dump(self.__cache, f, indent=2)

    def get_asset_pair_for_eur(self, asset):
        normalized_asset = asset.replace(".S", "")  # Handle staked assets like DOT.S

        # Return from cache if present
        if normalized_asset in self.__cache:
            return self.__cache[normalized_asset]

        # Fetch pairs from Kraken
        url = "https://api.kraken.com/0/public/AssetPairs"
        resp = requests.get(url).json()
        pairs = resp.get("result", {})

        for pair_name, pair_info in pairs.items():
            base = pair_info.get("base", "").replace("X", "").replace("Z", "")
            quote = pair_info.get("quote", "").replace("X", "").replace("Z", "")
            if base == normalized_asset and quote == "EUR":
                self.__cache[normalized_asset] = pair_name
                self.save_asset_pair_cache()
                return pair_name

        self.__cache[normalized_asset] = None
        self.save_asset_pair_cache()
        return None



class CurrencyPairs:
    def __init__(self) -> None:
        self.__pairs = []

    def add_pair(self, currency1: str, currency2: str, conversion_rate: float) -> None:
        self.__pairs.append(dict({
            'currency1': currency1.upper(),
            'currency2': currency2.upper(),
            'rate': conversion_rate,
        }))

    def fiat_names(self) -> list:
        fiat_names = unique([pair['currency1'] for pair in self.__pairs] + [pair['currency2'] for pair in self.__pairs])
        fiat_names.sort(reverse=False)

        return fiat_names

    def convert(self, from_currency, to_currency: str, amount: float) -> float:
        if amount == 0 or from_currency == to_currency:
            return round(amount, 2)

        for pair in self.__pairs:
            if pair['currency1'] == from_currency and pair['currency2'] == to_currency:
                return round(amount * pair['rate'], 2)
            elif pair['currency2'] == from_currency and pair['currency1'] == to_currency:
                return round(amount / pair['rate'], 2)
        else:
            raise Exception(f'Could not convert currency from {from_currency} to {to_currency}')
