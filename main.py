#!/usr/bin/env python

from abc import abstractmethod
from typing import Optional

from source.calculus import *
from source.output import *
from source.parsing import *
from source.currencies import *


if __name__ == '__main__':
    currencies = CurrencyPairs()
    currencies.add_pair('EUR', 'USD', 1.1326)
    currencies.add_pair('EUR', 'USDT', 1.1326)

    parser = KrakenCsvParser('EUR', currencies)
    downloads_path = 'imports/kraken/'
    calculator = Calculator(parser.parse('%strades.csv' % downloads_path))
    print(calculator.positions())
    print('\n')

    result = calculator.calculate()
    output_to_file(result, 'trades.pnl.csv')
    # result = list(filter(lambda x: x['position'] != 'test', result))
    print(*result, sep='\n')
    print('\n')

    result = calculator.summary(result)
    result = list(filter(lambda x: x['profit'] != 0 or x['loss'] != 0, result))
    print(*result, sep='\n')
    print('\n')
    output_to_file(result, 'trades.summary.csv')

    print('Total profit:', round(sum(item['profit'] for item in result), 2))
    print('Total loss:', round(sum(item['loss'] for item in result), 2))
    print('Total profit n loss:', round(sum(item['profit n loss'] for item in result), 2))
