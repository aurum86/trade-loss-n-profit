#!/usr/bin/env python

import time
import hmac
import hashlib
import base64
import requests
import urllib.parse
import pandas as pd
from datetime import datetime
from time import sleep
from dotenv import load_dotenv
import os
from source.ledger_cache import *
from source.currencies import *
from source.results_cache import *

if __name__ == '__main__':

    load_dotenv()

    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")

    if not API_KEY or not API_SECRET:
        raise ValueError("API_KEY or API_SECRET not set in .env file")


    # --------------------------------------
    def kraken_api_call(uri_path, data=None, retries=3):
        url = "https://api.kraken.com"
        api_nonce = str(int(time.time() * 1000))
        data = data or {}
        data['nonce'] = api_nonce
        post_data = urllib.parse.urlencode(data)
        message = (api_nonce + post_data).encode()
        sha256 = hashlib.sha256(message).digest()
        api_path = (uri_path).encode()
        secret = base64.b64decode(API_SECRET)
        hmac_key = hmac.new(secret, api_path + sha256, hashlib.sha512)
        headers = {
            'API-Key': API_KEY,
            'API-Sign': base64.b64encode(hmac_key.digest()),
        }

        # Retry logic in case of failure
        for attempt in range(retries):
            try:
                response = requests.post(url + uri_path, headers=headers, data=data)
                response.raise_for_status()  # Check if the request was successful
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    sleep(2)  # Wait before retrying
                    return None
                else:
                    raise
        return None


    def get_ledgers(ledger_type, reset_cache=False):
        if reset_cache:
            print("♻️ Resetting cache...")
            cached = {}
        else:
            cached = load_cached_ledgers(ledger_type)

        cached_ids = set(cached.keys())
        latest_cached_time = max((entry["time"] for entry in cached.values()), default=0)
        earliest_cached_time = min((entry["time"] for entry in cached.values()), default=0)

        print(f"🧠 Loaded {len(cached)} cached '{ledger_type}' entries")
        print(f"earliest time: {datetime.fromtimestamp(earliest_cached_time)}")
        print(f"latest time: {datetime.fromtimestamp(latest_cached_time).isoformat()}")

        offset = 0
        new_ledgers = {}

        while True:
            result = kraken_api_call('/0/private/Ledgers', {'type': ledger_type, 'ofs': offset})
            if 'error' in result and result['error']:
                print("Klaida:", result['error'])
                break

            entries = result['result']['ledger']
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
        save_cached_ledgers(ledger_type, merged)
        return list(merged.values())


    # --------------------------------------
    # 💶 Gauti istorinį kursą (Kraken public API)
    # --------------------------------------
    def get_price(pair, timestamp):
        url = f"https://api.kraken.com/0/public/OHLC?pair={pair}&interval=1440&since={int(timestamp)}"
        try:
            resp = requests.get(url).json()
            result_key = list(resp["result"].keys())[0]
            ohlc_data = resp["result"][result_key]
            if not ohlc_data:
                return None
            return float(ohlc_data[0][4])  # Close kaina for better accuracy
        except Exception as e:
            print(f"Error fetching price for {pair} at {timestamp}: {e}")
            return None


    # --------------------------------------
    # 🚀 Vykdymas
    # --------------------------------------
    ledger_type = "staking"
    load_asset_pair_cache()
    partial_results = load_partial_results(ledger_type)
    done_ids = {entry["id"] for entry in partial_results}

    staking_data = get_ledgers(ledger_type)
    records = []

    for entry in staking_data:
        print(".", end='')
        asset = entry['asset']
        amount = float(entry['amount'])
        timestamp = int(entry['time'])
        dt = datetime.utcfromtimestamp(timestamp)

        if asset == 'ZEUR' or asset == 'EUR':
            eur_rate = 1.0
        else:
            pair = get_asset_pair_for_eur(asset)
            if not pair:
                print(f"⚠️ No EUR pair found for asset {asset}")
                continue

            eur_rate = get_price(pair, timestamp)
            time.sleep(1.2)

        eur_value = amount * eur_rate if eur_rate else None

        records.append({
            'timestamp': dt,
            'asset': asset,
            'amount': amount,
            'eur_rate': eur_rate,
            'value_eur': eur_value
        })

    # 💾 Išsaugome CSV
    df = pd.DataFrame(records)
    df.to_csv("staking_is_kraken_api.csv", index=False)

    print(f"💰 Bendra staking pajamų suma (EUR): {df['value_eur'].sum():.2f}")
