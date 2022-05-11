#!/usr/bin/env python

from abc import abstractmethod
from typing import Optional

from source.calculus import *
from source.output import *
from source.parsing import *
from source.currencies import *

C_EUR_USD = 1.1326

if __name__ == '__main__':
    currencies = CurrencyPairs()
    currencies.add_pair('EUR', 'USD', C_EUR_USD)
    currencies.add_pair('EUR', 'USDT', C_EUR_USD)

    parser = KrakenCsvParser('EUR', currencies)
    downloads_path = 'imports/kraken/'
    result = parser.parse('%strades.csv' % downloads_path)
    # result = list(filter(lambda x: x['position'] == 'AVAXEUR', result))

    calculator = Calculator(result, ignore_negative_balance=True)
    positions = calculator.positions()
    print(positions)
    print('\n')

    result = calculator.calculate()

    import shutil
    import os
    if os.path.isdir('output'):
        shutil.rmtree('output')

    output_to_file(result, 'trades.pnl.csv')

    for position in positions:
        position_result = list(filter(lambda x: x['position'] == position, result))
        output_to_file(position_result, f'positions{os.sep}trades.{position}.csv')

    result = calculator.summary(result)
    # result = list(filter(lambda x: x['profit'] == 0 and x['loss'] == 0, result))
    print(*result, sep='\n')
    print('\n')
    output_to_file(result, 'trades.summary.csv')

    print('Total profit:', round(sum(item['profit'] for item in result), 2))
    print('Total loss:', round(sum(item['loss'] for item in result), 2))
    print('Total profit n loss:', round(sum(item['profit n loss'] for item in result), 2))
