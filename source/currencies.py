from source.utils import unique


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
            return round(amount, 2)

        for pair in self.__pairs:
            if pair['currency1'] == from_currency and pair['currency2'] == to_currency:
                return round(amount * pair['rate'], 2)
            elif pair['currency2'] == from_currency and pair['currency1'] == to_currency:
                return round(amount / pair['rate'], 2)
        else:
            raise Exception(f'Could not convert currency from {from_currency} to {to_currency}')
