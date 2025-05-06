#!/usr/bin/env python

import time
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from source.api_kraken import KrakenApi
from source.ledger_cache import *
from source.currencies import *
from source.results_cache import *
from source.kraken_ledger import KrakenLedger
from source.transactions import Transactions

cached_results = ResultsCache("output")

def format_results(ledger_type):
    partial_results = cached_results.load_partial_results(ledger_type)
    df = pd.DataFrame(partial_results)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp')
    df["value_eur"] = df["value_eur"].round(2)
    df["eur_rate"] = df["eur_rate"].round(5)
    df['year'] = df['timestamp'].dt.year

    return df


def generate_output(df):
    global year
    for year, group in df.groupby('year'):
        filename = f"report_in_eur_{ledger_type}_{year}.csv.csv"
        group.to_csv(os.path.join("output", filename), index=False)
        print(f"✅ Saved {filename}")
        print(f"💰 Total sum (EUR): {group['value_eur'].sum():.2f}")

    df.to_csv(os.path.join("output", f"report_in_eur_{ledger_type}.csv"), index=False)
    print(f"💰 Total sum (EUR): {df['value_eur'].sum():.2f}")


def parse_entry(entry):
    asset = None
    pair = None
    if 'asset' in entry and 'amount' in entry:
        transaction_id = entry['refid']
        asset = entry['asset']
        amount = float(entry['amount'])
        direction = 1
    elif 'vol' in entry and 'pair' in entry:
        transaction_id = entry['trade_id']
        pair = entry['pair']
        amount = float(entry['vol'])
        direction = 1 if entry['type'] == 'sell' else -1
    else:
        print("Unknown format: ", entry)
        return None, None

    return (
        transaction_id, pair, asset,
        amount, direction, entry,
    )


def get_rate_in_eur(ledger_type, pair, asset):
    if ledger_type == "staking":
        if asset in ['ZEUR', 'EUR']:
            result = 1.0
        else:
            pair = cached_asset_pairs.get_asset_pair_for_eur(asset)
            if not pair:
                print(f"⚠️ No EUR pair for asset: {asset}")
                return None
            result = kraken_ledger.get_price(pair, timestamp)
            if result is None:
                print(f"⚠️ No price data for {pair} at {dt}")
                return None
            time.sleep(1.2)
    else:
        result = kraken_ledger.get_price(pair, timestamp)

    return result


if __name__ == '__main__':

    load_dotenv()

    force_update = True
    # force_update = False

    # ledger_type = "staking"
    ledger_type = "trading"

    cached_ledger = LedgerCache("output")
    cached_asset_pairs = AssetPairs("output")

    if not os.getenv("API_KEY") or not os.getenv("API_SECRET"):
        raise ValueError("API_KEY or API_SECRET not set in .env file")

    kraken_api = KrakenApi(os.getenv("API_KEY"), os.getenv("API_SECRET"))
    kraken_ledger = KrakenLedger(kraken_api)
    transactions = Transactions(cached_ledger, kraken_ledger)
    cached_asset_pairs.load_asset_pair_cache()
    partial_results_list = cached_results.load_partial_results(ledger_type)
    partial_results = {
        entry["refid"]: entry for entry in partial_results_list
    }
    done_ids = set(partial_results.keys())

    staking_data = transactions.get_ledgers(ledger_type)
    records = []

    print(f"{len(done_ids)} out of {len(staking_data)} is calculated")

    dot_counter = 0
    for entry in staking_data:
        print(".", end="", flush=True)
        dot_counter += 1
        if dot_counter % 100 == 0:
            print(f"{dot_counter}")

        (
            ledger_id, pair, asset,
            amount, direction, entry,
        ) = parse_entry(entry)
        if ledger_id in done_ids and not force_update:
            continue  # Already processed

        timestamp = int(entry['time'])
        dt = datetime.utcfromtimestamp(timestamp)

        try:
            if force_update and bool(partial_results):
                _partial_result = partial_results.get(ledger_id, None)
                if _partial_result is None:
                    eur_rate = get_rate_in_eur(ledger_type, pair, asset)
                else:
                    eur_rate = _partial_result['eur_rate']
            else:
                eur_rate = get_rate_in_eur(ledger_type, pair, asset)
            if eur_rate is None:
                continue

            eur_value = amount * eur_rate if eur_rate else None

            record = {
                'refid': ledger_id,
                'timestamp': dt.isoformat(),
                'asset': asset,
                'amount': amount,
                'eur_rate': eur_rate,
                'value_eur': eur_value,
                'entry': entry,
            }

            partial_results[ledger_id] = record
            cached_results.save_partial_results(ledger_type, list(partial_results.values()))

        except Exception as e:
            print(f"❌ Error on {ledger_id}: {e}")
            continue

    df = format_results(ledger_type)
    generate_output(df)
