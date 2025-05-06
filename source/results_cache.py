import json
import os

class ResultsCache:
    def __init__(self, directory):
        self.__dir = directory

    def __get_partial_cache_file_path(self, ledger_type):
        os.makedirs(self.__dir, exist_ok=True)
        return os.path.join(self.__dir, f"partial_results_{ledger_type}.json")

    def load_partial_results(self, ledger_type):
        file_path = self.__get_partial_cache_file_path(ledger_type)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                if os.path.getsize(file_path) == 0:
                    return []
                return json.load(f)
        return []

    def save_partial_results(self, ledger_type, data):
        with open(self.__get_partial_cache_file_path(ledger_type), "w") as f:
            json.dump(data, f, indent=2)
