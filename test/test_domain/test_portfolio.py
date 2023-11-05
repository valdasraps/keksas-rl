import pytest
from domain.portfolio import Portfolio


class TestPortfolio:

    @pytest.fixture
    def initial_balance(self) -> float:
        return 1000.0

    @pytest.mark.parametrize('leverage', [1.0, 2.0, 3.0])
    def test_balance_initializes_ok(self, initial_balance: float, leverage: float) -> None:
        portfolio = Portfolio(initial_balance=initial_balance, leverage=leverage)
        assert portfolio.free == initial_balance * leverage
        assert portfolio.equity == initial_balance * leverage
        assert portfolio.balance(price=10000.0) == initial_balance * leverage
        assert portfolio.long_position_rate == 0.0
        assert portfolio.short_position_rate == 0.0

    @pytest.mark.parametrize('leverage', [1.0, 2.0, 3.0])
    def test_long_rates_are_calculated_ok(self, initial_balance: float, leverage: float) -> None:
        portfolio = Portfolio(initial_balance=initial_balance, leverage=leverage)

        portfolio.add_long(price=100.0, balance_rate=0.2)

        assert portfolio.long_position_rate == 0.2
        assert portfolio.short_position_rate == 0.0
        assert portfolio.free == initial_balance * leverage * 0.8
        assert portfolio.equity == initial_balance * leverage
        assert portfolio.balance(price=100.0) == initial_balance * leverage
        assert portfolio.long_pnl_rate(price=100.0) == 0.0

        assert portfolio.long_pnl_rate(price=50.0) == -0.5
        assert portfolio.balance(price=50.0) == initial_balance * leverage - 100.0 * leverage

        assert portfolio.long_pnl_rate(price=110.0) == 0.1
        assert portfolio.balance(price=110.0) == initial_balance * leverage + 20.0 * leverage

    @pytest.mark.parametrize('leverage', [1.0, 2.0, 3.0])
    def test_short_rates_are_calculated_ok(self, initial_balance: float, leverage: float) -> None:
        portfolio = Portfolio(initial_balance=initial_balance, leverage=leverage)

        portfolio.add_short(price=100.0, balance_rate=0.3)

        assert portfolio.long_position_rate == 0.0
        assert portfolio.short_position_rate == 0.3
        assert portfolio.free == initial_balance * leverage * 0.7
        assert portfolio.equity == initial_balance * leverage
        assert portfolio.balance(price=100.0) == initial_balance * leverage
        assert portfolio.short_pnl_rate(price=100.0) == 0.0

        assert portfolio.short_pnl_rate(price=50.0) == 0.5
        assert portfolio.balance(price=50.0) == initial_balance * leverage + 150.0 * leverage

        assert portfolio.short_pnl_rate(price=110.0) == -0.1
        assert portfolio.balance(price=110.0) == initial_balance * leverage - 30.0 * leverage

    @pytest.mark.parametrize('leverage', [1.0, 2.0, 3.0])
    def test_full_long_positions_are_open_closed_ok(self, initial_balance: float, leverage: float) -> None:
        portfolio = Portfolio(initial_balance=initial_balance, leverage=leverage)

        portfolio.add_long(price=100.0, balance_rate=0.2)
        portfolio.remove_long(price=110.0, amount_rate=1.0)

        assert portfolio.free == (initial_balance + 20.0 * leverage) * leverage
        assert portfolio.equity == portfolio.free
        assert portfolio.long_position_rate == 0.0

    @pytest.mark.parametrize('leverage', [1.0, 2.0, 3.0])
    def test_full_short_positions_are_open_closed_ok(self, initial_balance: float, leverage: float) -> None:
        portfolio = Portfolio(initial_balance=initial_balance, leverage=leverage)

        portfolio.add_short(price=100.0, balance_rate=0.2)
        portfolio.remove_short(price=90.0, amount_rate=1.0)

        assert portfolio.free == (initial_balance + 20.0 * leverage) * leverage
        assert portfolio.equity == portfolio.free
        assert portfolio.long_position_rate == 0.0

    @pytest.mark.parametrize(('leverage','equities'), [
        (1.0, [1010.0, 1022.1, 1041.0,]),
        (2.0, [2040.0, 2088.0, 2166.0,]),
        (3.0, [3090.0, 3200.0, 3375.0,])
    ])
    def test_partly_long_positions_are_open_closed_ok(self,
                                                      initial_balance: float,
                                                      leverage: float,
                                                      equities: list[float]) -> None:
        portfolio = Portfolio(initial_balance=initial_balance, leverage=leverage)

        portfolio.add_long(price=100.0, balance_rate=0.2)
        portfolio.remove_long(price=110.0, amount_rate=0.5)

        assert portfolio.equity == equities[0]
        assert portfolio.long_position_rate == pytest.approx(0.09, abs=0.01)

        portfolio.add_long(price=110.0, balance_rate=0.2)

        assert portfolio.equity == pytest.approx(equities[0], abs=1)
        assert portfolio.long_position_rate == pytest.approx(0.3, abs=0.01)

        portfolio.remove_long(price=115.0, amount_rate=0.5)

        assert portfolio.equity == pytest.approx(equities[1], abs=1)
        assert portfolio.long_position_rate == pytest.approx(0.14, abs=0.01)

        portfolio.remove_long(price=120.0, amount_rate=1.0)

        assert portfolio.equity == pytest.approx(equities[2], abs=1)
        assert portfolio.long_position_rate == pytest.approx(0.0)

    @pytest.mark.parametrize(('leverage','equities'), [
        (1.0, [1010.0, 1023.1, 1044.5,]),
        (2.0, [2040.0, 2092.8, 2178.6,]),
        (3.0, [3090.0, 3209.5, 3403.5,])
    ])
    def test_partly_short_positions_are_open_closed_ok(self,
                                                       initial_balance: float,
                                                       leverage: float,
                                                       equities: list[float]) -> None:
        portfolio = Portfolio(initial_balance=initial_balance, leverage=leverage)

        portfolio.add_short(price=100.0, balance_rate=0.2)
        portfolio.remove_short(price=90.0, amount_rate=0.5)

        assert portfolio.equity == pytest.approx(equities[0], abs=1)
        assert portfolio.short_position_rate == pytest.approx(0.09, abs=0.01)

        portfolio.add_short(price=90.0, balance_rate=0.2)

        assert portfolio.equity == pytest.approx(equities[0], abs=1)
        assert portfolio.short_position_rate == pytest.approx(0.30, abs=0.01)

        portfolio.remove_short(price=85.0, amount_rate=0.5)

        assert portfolio.equity == pytest.approx(equities[1], abs=1)
        assert portfolio.short_position_rate == pytest.approx(0.14, abs=0.01)

        portfolio.remove_short(price=80.0, amount_rate=1.0)

        assert portfolio.equity == pytest.approx(equities[2], abs=1)
        assert portfolio.short_position_rate == pytest.approx(0.0)

    @pytest.mark.parametrize(('leverage', 'price', 'balance', 'liquidated'), [
        (1.0, 100.0, 1000.0, False),
        (1.0, 90.0, 950.0, False),
        (1.0, 1.0, 505.0, False),
        (2.0, 100.0, 2000.0, False),
        (2.0, 90.0, 1900.0, False),
        (2.0, 5.0, 1050.0, True),
        (10.0, 100.0, 10000.0, False),
        (10.0, 90.0, 9500.0, True),
        (10.0, 5.0, 5250.0, True),
    ])
    def test_position_liquidates_ok(self,
                                    initial_balance: float,
                                    leverage: float,
                                    price: float,
                                    balance: float,
                                    liquidated: bool) -> None:
        portfolio = Portfolio(initial_balance=initial_balance, leverage=leverage)
        portfolio.add_long(price=100.0, balance_rate=0.5)

        assert portfolio.equity == initial_balance * leverage
        assert portfolio.balance(price=price) == balance
        assert portfolio.liquidate(price=price) is liquidated

        if liquidated:
            assert portfolio.equity == 0.0
            assert portfolio.balance(price=price) == 0.0
            assert portfolio.free == 0.0
        else:
            assert portfolio.balance(price=price) == balance
