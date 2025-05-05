import os
import json

CACHE_DIR = "kraken_ledger_cache"

def get_cache_file_path(ledger_type):
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"ledgers_{ledger_type}.json")

def load_cached_ledgers(ledger_type):
    path = get_cache_file_path(ledger_type)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_cached_ledgers(ledger_type, ledgers):
    path = get_cache_file_path(ledger_type)
    with open(path, "w") as f:
        json.dump(ledgers, f, indent=2)
