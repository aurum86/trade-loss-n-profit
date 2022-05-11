from abc import abstractmethod
from typing import Optional
from source.currencies import *


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
            'price wo fee': round(abs(price - fee if operation == 'buy' else fee - price), 2),
            'price': price,
            'cost': cost,
            'fee': fee,
            'date': date,
            'debug': debug
        }))


class KrakenCsvParser(AbstractParser):
    F_PAIR = 'pair'
    F_COST = 'cost'
    F_FEE = 'fee'
    F_PRICE = 'price'
    F_VOLUME = 'vol'
    F_TIME = 'time'
    F_TYPE = 'type'

    FIELD_LIST = [
        F_PAIR,
        F_COST,
        F_FEE,
        F_PRICE,
        F_VOLUME,
        F_TIME,
        F_TYPE,
    ]

    def __init__(self, main_currency: str, currencies: CurrencyPairs) -> None:
        super().__init__()
        self.__main_currency: str = main_currency.upper()
        self.__currencies: CurrencyPairs = currencies

    def parse(self, file_path: str) -> list:
        import csv
        with open(file_path) as csv_file:
            test = csv.DictReader(csv_file, delimiter=',')
            self.__validate_input_fields(list(test.fieldnames))
            for row in list(test)[1:]:
                position = row[self.F_PAIR]

                price = float(row[self.F_PRICE])
                fee = float(row[self.F_FEE])
                price_orig = price
                fee_orig = fee

                volume = float(row[self.F_VOLUME])
                cost = float(row[self.F_COST])
                try:
                    volume = cost / price if price == 0 else volume
                except:
                    print(f'Division by zero problem: {row}')

                fiat_name = self.__find_fiat_name(position)
                if fiat_name:
                    price = self.__currencies.convert(fiat_name, self.__main_currency, price)
                    fee = self.__currencies.convert(fiat_name, self.__main_currency, fee)

                self._append(
                    position, row[self.F_TYPE], volume,
                    price, cost, fee,
                    row[self.F_TIME]
                )
        return self._get_data()

    def __validate_input_fields(self, fields: list) -> None:
        missing_fields = set(self.FIELD_LIST) - set(fields)
        if missing_fields:
            raise Exception(f'Missing required fields: {missing_fields}')

    def __find_fiat_name(self, position: str) -> Optional[str]:
        for name in self.__currencies.fiat_names():
            if position.endswith(name):
                return name
        else:
            return None
