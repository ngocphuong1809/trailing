from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

class RSI2(Strategy):
    def __init__(self):
        super().__init__()

        self.vars["fast_sma_period"] = 5
        self.vars["slow_sma_period"] = 200
        self.vars["rsi_period"] = 2
        self.vars["rsi_ob_threshold"] = 90
        self.vars["rsi_os_threshold"] = 10

    def hyperparameters(self):
        return [
                {'name':'stop_loss', 'type': float, 'min': .5, 'max': .99, 'default': .9},
                {'name':'take_profit', 'type': float, 'min': 1.1, 'max': 1.2, 'default': 1.1},
        ]

    @property
    def fast_sma(self):
        return ta.sma(self.candles, self.vars["fast_sma_period"])

    @property
    def slow_sma(self):
        return ta.sma(self.candles, self.vars["slow_sma_period"])

    @property
    def rsi(self):
        return ta.rsi(self.candles, self.vars["rsi_period"])

    def should_long(self) -> bool:
        # Enter long if current price is above sma(200) and RSI(2) is below oversold threshold
        return self.price > self.slow_sma and self.rsi <= self.vars["rsi_os_threshold"]

    def should_short(self) -> bool:
        # Enter long if current price is below sma(200) and RSI(2) is above oversold threshold
        return self.price < self.slow_sma and self.rsi >= self.vars["rsi_ob_threshold"]

    def should_cancel(self) -> bool:
        return False

    def go_long(self):
        # # Open long position and use entire balance to buy
        risk_perc = 3
        capital = 10000
        # Open long position and use entire balance to buy
        qty = utils.risk_to_qty(capital, risk_perc, self.price, self.fee_rate)
        self.buy = qty, self.price
        self.stop_loss = qty, (self.price * self.hp['stop_loss'])        # Willing to lose 10%
        self.take_profit = qty, (self.price * self.hp['take_profit'])     # Take profits at 10%    

    def go_short(self):
        # # Open short position and use entire balance to sell
        risk_perc = 3
        capital = 10000
        # Open long position and use entire balance to buy
        qty = utils.risk_to_qty(capital, risk_perc, self.price, self.fee_rate)
        # self.sell = qty, self.price
        self.sell = [
            (qty/2, self.price*1.1),
            (qty/2, self.price*1.2)
        ]
        
    def update_position(self):
        # Exit long position if price is above sma(5)
        if self.is_long and self.price > self.fast_sma:
            self.liquidate()
    
        # Exit short position if price is below sma(5)
        if self.is_short and self.price < self.fast_sma:
            self.liquidate()
