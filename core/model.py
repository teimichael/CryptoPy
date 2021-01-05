# Order model
def Order(symbol: str, type: str, side: str, amount: float, price=None, timestamp=None) -> dict:
    return {
        'symbol': symbol,
        'type': type,
        'side': side,
        'amount': amount,
        'price': price,
        'timestamp': timestamp
    }


# Performance information model
class PerfInfo:

    def __init__(self):
        # PnL
        self.pnl = 0
        # Long PnL
        self.long_pnl = 0
        # Short PnL
        self.short_pnl = 0
        # Gross profit
        self.gross_profit = 0
        # Long gross profit
        self.long_gross_profit = 0
        # Short gross profit
        self.short_gross_profit = 0
        # Gross loss
        self.gross_loss = 0
        # Long gross profit
        self.long_gross_loss = 0
        # Short gross profit
        self.short_gross_loss = 0
        # Win order number
        self.win = 0
        # Long win order number
        self.win_long = 0
        # Short win order number
        self.win_short = 0
        # Lose order number
        self.loss = 0
        # Long loss order number
        self.loss_long = 0
        # Short win order number
        self.loss_short = 0
