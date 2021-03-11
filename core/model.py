# Order model
def Order(id: int, symbol: str, type: str, side: str, amount: float, price=None, timestamp=None,
          status="unfilled") -> dict:
    return {
        'id': id,
        'clientOrderId': None,
        'symbol': symbol,
        'type': type,
        'side': side,
        'amount': amount,
        'price': price,
        'timestamp': timestamp,
        'status': status
    }


# Performance information model
class PerfInfo:

    def __init__(self):
        # PnL
        self.pnl = 0
        # Max PnL
        self.pnl_max = 0
        # Min PnL
        self.pnl_min = 0
        # Max Cumulative PnL
        self.cum_pnl_max = 0
        # Min Cumulative PnL
        self.cum_pnl_min = 0
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
        # PnL History
        self.pnl_history = []
        # Cumulative PnL History
        self.cum_pnl_history = []
        # Timestamps
        self.timestamps = []
