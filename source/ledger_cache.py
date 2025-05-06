import os
import json

CACHE_DIR = "kraken_ledger_cache"

class LedgerCache:
    def __init__(self, directory) -> None:
        self.__dir = directory

    def __get_cache_file_path(self, ledger_type):
        path = os.path.join(self.__dir, CACHE_DIR)
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, f"ledgers_{ledger_type}.json")

    def load_cached_ledgers(self, ledger_type):
        path = self.__get_cache_file_path(ledger_type)
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def save_cached_ledgers(self, ledger_type, ledgers):
        path = self.__get_cache_file_path(ledger_type)
        with open(path, "w") as f:
            json.dump(ledgers, f, indent=2)
