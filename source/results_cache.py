import json
import os

def get_partial_cache_file_path(ledger_type):
    # os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join("", f"staking_partial_results_{ledger_type}.json")

def load_partial_results(ledger_type):
    if os.path.exists(get_partial_cache_file_path(ledger_type)):
        with open(get_partial_cache_file_path(ledger_type), "r") as f:
            return json.load(f)
    return []

def save_partial_results(ledger_type, data):
    with open(get_partial_cache_file_path(ledger_type), "w") as f:
        json.dump(data, f, indent=2)
