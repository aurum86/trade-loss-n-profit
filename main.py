#!/usr/bin/env python
from abc import abstractmethod
from typing import Optional


def unique(list1) -> list:
    output = set()
    for x in list1:
        output.add(x)
    return list(output)


class AbstractParser:
    def __init__(self) -> None:
        self.__data: list = []

    @abstractmethod
    def parse(self, file_path: str) -> list:
        return self.__data

    def _get_data(self) -> list:
        return self.__data

    def _append(self,
                position: str, operation: str, volume: float,
                price: float, cost: float, fee: float,
                date: str, debug: str = None
                ) -> None:
        self.__data.append(dict({
            'position': position,
            'type': operation,
            'volume': volume,
            'price wo fee': abs(price - fee if operation == 'buy' else fee - price),
            'price': price,
            'cost': cost,
            'fee': fee,
            'date': date,
            'debug': debug
        }))


class CurrencyPairs:
    def __init__(self) -> None:
        self.__pairs = []

    def add_pair(self, currency1: str, currency2: str, conversion_rate: float) -> None:
        self.__pairs.append(dict({
            'currency1': currency1.upper(),
            'currency2': currency2.upper(),
            'rate': conversion_rate,
        }))

    def fiat_names(self) -> list:
        fiat_names = unique([pair['currency1'] for pair in self.__pairs] + [pair['currency2'] for pair in self.__pairs])
        fiat_names.sort(reverse=False)

        return fiat_names

    def convert(self, from_currency, to_currency: str, amount: float) -> float:
        if amount == 0 or from_currency == to_currency:
            return amount

        for pair in self.__pairs:
            if pair['currency1'] == from_currency and pair['currency2'] == to_currency:
                return round(amount * pair['rate'], 2)
            elif pair['currency2'] == from_currency and pair['currency1'] == to_currency:
                return round(amount / pair['rate'], 2)
        else:
            raise Exception(f'Could not convert currency from {from_currency} to {to_currency}')


class KrakenCsvParser(AbstractParser):
    def __init__(self, main_currency: str, currencies: CurrencyPairs) -> None:
        super().__init__()
        self.__main_currency: str = main_currency.upper()
        self.__currencies: CurrencyPairs = currencies

    def parse(self, file_path: str) -> list:
        import csv
        with open(file_path) as csv_file:
            test = csv.reader(csv_file, delimiter=',')
            for row in list(test)[1:]:
                position = row[2]

                price = float(row[6])
                fee = float(row[8])
                price_orig = price
                fee_orig = fee

                volume = float(row[9])
                cost = float(row[7])
                volume = volume if price == 0 else cost / price

                fiat_name = self.__get_fiat_name(position)
                if fiat_name:
                    price = self.__currencies.convert(fiat_name, self.__main_currency, price)
                    fee = self.__currencies.convert(fiat_name, self.__main_currency, fee)

                self._append(
                    position, row[4], volume,
                    price, cost, fee,
                    row[3]
                )
        return self._get_data()

    def __get_fiat_name(self, position: str) -> Optional[str]:
        for name in self.__currencies.fiat_names():
            if position.endswith(name):
                return name
        else:
            return None
            # raise Exception(f'Fiat name not found by pair: {position}')


def write_to_file(data: list, file_path: str) -> None:
    import csv
    if not data:
        return

    keys = data[0].keys()
    with open(file_path, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


class Calculator:
    def __init__(self, items: list):
        self.__items = items
        self.__result: list = []
        self.__verbose = False
        self.__ignore_negative_balance = False

    def positions(self) -> list:
        positions = unique([row['position'] for row in self.__items])
        positions.sort(reverse=False)

        return positions

    def summary(self, items: list = None) -> list:
        if not items:
            items = self.calculate()

        report = []
        for position in self.positions():
            orders = list(filter(lambda row: row['position'] == position, items))
            profit = 0
            loss = 0
            if not orders:
                continue
            for order in orders:
                value = order['profit']
                profit += value if value and value > 0 else 0
                loss += value if value and value < 0 else 0

            last_order = orders[-1]
            pnl_list = list(filter(None, [order.get('cumulative profit') for order in orders]))
            pnl = pnl_list[-1] if pnl_list else 0
            report.append({
                'position': last_order['position'],
                'transactions': len(orders),
                'profit': round(profit, 2),
                'loss': round(loss, 2),
                'profit n loss': pnl
            })

        return report

    def calculate(self) -> list:
        self.__result = []
        self.__items.sort(key=lambda row: row['date'], reverse=False)

        total_pnl = 0
        for position in self.positions():
            orders = list(filter(lambda row: row['position'] == position, self.__items))
            if orders:
                pnl = self.__process(orders)
                total_pnl += pnl
                # print(f'Total pnl: {pnl} for {position}')
                continue
            raise Exception('No data')
        # print(f'Grand total pnl: {total_pnl} for all positions')
        return self.__result

    def __process(self, orders: list) -> float:
        current_portfolio = []
        pnl = 0
        for order in orders:
            order['profit'] = None
            order['cumulative profit'] = None
            order['remaining volume'] = order['volume']

            if order['type'] == 'buy':
                current_portfolio.append(order)
            else:
                previous_pnl = pnl
                pnl = self.__process_sale(current_portfolio, order, pnl)
                order['profit'] = pnl - previous_pnl
                order['cumulative profit'] = round(pnl, 2)

            self.__result.append(order)
        return pnl

    def __process_sale(self, portfolio: list, sell_order, pnl=0) -> float:
        sell_order_amount = sell_order['volume']
        sell_order_price = sell_order['price']
        if self.__verbose:
            print(
                f'Processing sell order on {sell_order["date"]} for {sell_order_amount} shares at {sell_order_price} price')
        while sell_order_amount > 0:
            if not portfolio:
                message = f"Trying to sell more shares than there are bought ones: {sell_order['position']} @ {sell_order['date']}"
                if self.__ignore_negative_balance:
                    print(message)
                else:
                    # raise Exception(message)
                    break
            buy_order_amount = portfolio[0]['remaining volume']
            buy_order_price = portfolio[0]['price']
            buy_order_date = portfolio[0]['date']
            price_difference = sell_order_price - buy_order_price
            sold_amount = min(sell_order_amount, buy_order_amount)
            sell_order_amount -= sold_amount
            pnl += sold_amount * price_difference
            if self.__verbose:
                print(
                    f"Selling {sold_amount:.2f} of shares that were bought on {buy_order_date} @ {buy_order_price:.2f} at price {sell_order_price:.2f}, (price difference {price_difference:.2f}), total pnl {pnl:.2f}")

            if buy_order_amount > sold_amount:
                portfolio[0]['remaining volume'] -= sold_amount
            else:
                portfolio.pop(0)
        return pnl


def output_to_file(result, file_name):
    output_path = 'output/kraken/'
    import os
    os.makedirs(output_path, 0o777, True)
    try:
        os.chmod('output', 0o777)
        os.chmod(output_path, 0o777)
    except:
        pass

    write_to_file(result, output_path + file_name)
    try:
        os.chmod(output_path + file_name, 0o666)
    except:
        pass


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
