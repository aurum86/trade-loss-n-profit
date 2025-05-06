from collections import deque
from datetime import datetime
import csv

class InventoryCalculator:
    def __init__(self):
        self.__inventory = {}
        self.__taxable_events = []

    def get_taxable_events(self):
        return self.__taxable_events

    def add_purchase(self, asset, amount, price_eur, timestamp):
        self.__inventory.setdefault(asset, deque()).append({
            "amount": amount,
            "price_eur": price_eur,
            "timestamp": timestamp,
        })
    
    def process_sale(self, asset, amount_sold, sell_price_eur, timestamp):
        fifo = self.__inventory.get(asset, deque())
        remaining = amount_sold
        cost_basis = 0.0
        sold_lots = []
    
        while remaining > 0 and fifo:
            lot = fifo[0]
            matched = min(lot['amount'], remaining)
            cost_basis += matched * lot['price_eur']
            sold_lots.append((lot['timestamp'], matched, lot['price_eur']))
            if matched == lot['amount']:
                fifo.popleft()
            else:
                lot['amount'] -= matched
            remaining -= matched
    
        gain = amount_sold * sell_price_eur - cost_basis
    
        self.__taxable_events.append({
            'sell_timestamp': timestamp,
            'sell_date': timestamp.strftime('%Y-%m-%d'),
            'asset': asset,
            'amount': f"{round(amount_sold, 8):.8f}",
            'sell_price': round(sell_price_eur, 2),
            'cost_basis': round(cost_basis, 2),
            'gain_eur': round(gain, 2),
            'related_buys': [
                {
                    'timestamp': dt.isoformat(),
                    'amount': f"{round(amt, 8):.8f}",
                    'price': price
                } for dt, amt, price in sold_lots
            ],
        })
