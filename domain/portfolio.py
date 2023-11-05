import typing


class _Position:

    def __init__(self, side: typing.Literal[1, -1]) -> None:
        self.side = side
        self.price = 0.0
        self.amount = 0.0

    def add(self, price: float, amount: float) -> float:
        self.price = (self.price * self.amount + price * amount) / (self.amount + amount)
        self.amount += amount

        cost = price * amount
        return cost

    def remove(self, price: float, amount: float) -> tuple[float, float]:
        if amount > self.amount:
            raise ValueError(f'Not enough amount to remove: {amount} > {self.amount}')
        self.amount -= amount

        cost = self.price * amount
        pnl = (price - self.price) * amount * self.side

        if self.amount == 0.0:
            self.price = 0.0
        return cost, pnl

    @property
    def cost(self) -> float:
        return self.price * self.amount

    def pnl(self, price: float) -> float:
        return (price - self.price) * self.amount * self.side

    def pnl_rate(self, price: float) -> float:
        return self.pnl(price=price) / self.cost


class Portfolio:

    def __init__(self, initial_balance: float, leverage: float = 1.0) -> None:
        self._initial_balance = initial_balance
        self._leverage = leverage

        self._free = initial_balance
        self._long = _Position(side=1)
        self._short = _Position(side=-1)

    def reset(self) -> None:
        self._free = self._initial_balance
        self._long = _Position(side=1)
        self._short = _Position(side=-1)

    @property
    def free(self) -> float:
        return self._free * self._leverage

    def add_long(self, price: float, balance_rate: float) -> None:
        self._add(position=self._long, price=price, balance_rate=balance_rate)

    def add_short(self, price: float, balance_rate: float) -> None:
        self._add(position=self._short, price=price, balance_rate=balance_rate)

    def _add(self, position: _Position, price: float, balance_rate: float) -> None:
        if balance_rate > 1.0:
            raise ValueError(f'Cannot spend more than 100% of balance: {balance_rate} > 1.0')

        amount = (self.balance(price=price) * balance_rate) / price
        cost = position.add(price=price, amount=amount)
        self._free -= cost / self._leverage

    def remove_long(self, price: float, amount_rate: float) -> None:
        self._remove(position=self._long, price=price, amount_rate=amount_rate)

    def remove_short(self, price: float, amount_rate: float) -> None:
        self._remove(position=self._short, price=price, amount_rate=amount_rate)

    def _remove(self, position: _Position, price: float, amount_rate: float) -> None:
        if amount_rate > 1.0:
            raise ValueError(f'Cannot remove more than 100% of position: {amount_rate} > 1.0')

        amount = position.amount * amount_rate
        cost, pnl = position.remove(price=price, amount=amount)
        self._free += cost / self._leverage
        self._free += pnl

    @property
    def equity(self) -> float:
        return self._free * self._leverage + self._long.cost + self._short.cost

    def balance(self, price: float) -> float:
        return self.equity + self._long.pnl(price=price) + self._short.pnl(price=price)

    @property
    def long_position_rate(self) -> float:
        return self._long.cost / self.equity

    @property
    def short_position_rate(self) -> float:
        return self._short.cost / self.equity

    def long_pnl_rate(self, price: float) -> float:
        return self._long.pnl_rate(price=price)

    def short_pnl_rate(self, price: float) -> float:
        return self._short.pnl_rate(price=price)

    def liquidate(self, price: float) -> bool:
        common_pnl = self._long.pnl(price=price) + self._short.pnl(price=price)
        if common_pnl < 0.0 and abs(common_pnl) >= self._free:
            self._long = _Position(side=1)
            self._short = _Position(side=-1)
            self._free = 0.0
            return True
        return False
