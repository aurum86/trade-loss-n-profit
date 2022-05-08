from source.utils import unique


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
