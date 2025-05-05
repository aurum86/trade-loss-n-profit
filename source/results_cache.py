import json
import os

PARTIAL_RESULTS_FILE = "staking_partial_results.json"


def load_partial_results(ledger_type):
    if os.path.exists(PARTIAL_RESULTS_FILE):
        with open(PARTIAL_RESULTS_FILE, "r") as f:
            return json.load(f)
    return []

def save_partial_results(ledger_type, data):
    with open(PARTIAL_RESULTS_FILE, "w") as f:
        json.dump(data, f, indent=2)
