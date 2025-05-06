import time
from datetime import datetime

class Transactions:
    def __init__(self, cached_ledger, kraken_ledger):
        self.__cached_ledger = cached_ledger
        self.__kraken_ledger = kraken_ledger

    def get_ledgers(self, ledger_type, reset_cache=False):
        if reset_cache:
            print("♻️ Resetting cache...")
            cached = {}
        else:
            cached = self.__cached_ledger.load_cached_ledgers(ledger_type)

        cached_ids = set(cached.keys())
        latest_cached_time = max((entry["time"] for entry in cached.values()), default=0)
        earliest_cached_time = min((entry["time"] for entry in cached.values()), default=0)

        print(f"🧠 Loaded {len(cached)} cached '{ledger_type}' entries")
        print(f"earliest time: {datetime.fromtimestamp(earliest_cached_time)}")
        print(f"latest time: {datetime.fromtimestamp(latest_cached_time).isoformat()}")

        offset = 0
        new_ledgers = {}

        while True:
            ledger, result = self.__kraken_ledger.fetch_history(ledger_type, offset)
            if 'error' in result and result['error']:
                print("Error:", result['error'])
                break

            entries = result['result'][ledger]
            if not entries:
                break

            stop_fetching = False
            for ledger_id, entry in entries.items():
                if ledger_id in cached_ids or entry["time"] <= latest_cached_time:
                    stop_fetching = True
                    break
                new_ledgers[ledger_id] = entry

            if stop_fetching or len(entries) < 50:
                break

            offset += 50
            time.sleep(1)

        # Merge and save
        merged = {**cached, **new_ledgers}
        print(f"📦 Fetched {len(new_ledgers)} new entries. Total: {len(merged)}")
        self.__cached_ledger.save_cached_ledgers(ledger_type, merged)
        return list(merged.values())