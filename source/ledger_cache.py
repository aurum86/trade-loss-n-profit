import os
import json

class LedgerCache:
    def __init__(self, directory) -> None:
        self.__dir = directory

    def __get_cache_file_path(self, ledger_type):
        os.makedirs(self.__dir, exist_ok=True)
        return os.path.join(self.__dir, f"ledgers_{ledger_type}.json")

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
