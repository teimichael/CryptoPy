from core.model import PerfInfo

precision = 10


# TODO funding, fee, rate, etc.
def get_performance(orders) -> PerfInfo:
    perf = PerfInfo()
    if len(orders) < 1:
        return perf

    # Entry price
    entry_price = 0
    # Total long amount
    long_amount = 0
    # Total short amount
    short_amount = 0
    # Position type
    position_type = None
    for o in orders:
        if o['status'] != "filled":
            continue
        # First order determines position type
        if position_type is None:
            position_type = 'long' if o['side'] == 'buy' else 'short'
        if o['side'] == 'buy' and position_type == 'long':
            # Calculate total value
            total = entry_price * long_amount + o['amount'] * o['price']
            # Increase amount
            long_amount += o['amount']
            # Liquidate entry price
            entry_price = total / long_amount
        elif o['side'] == 'sell' and position_type == 'long':
            if long_amount > o['amount']:
                # Close long partially
                pnl = (o['price'] - entry_price) * o['amount']
                long_amount -= o['amount']
            elif long_amount == o['amount']:
                # Close long totally
                pnl = (o['price'] - entry_price) * long_amount
                long_amount = 0
                position_type = None
            else:
                # Close long totally and open short
                pnl = (o['price'] - entry_price) * long_amount
                long_amount = 0
                short_amount = o['amount'] - long_amount
                position_type = 'short'
            # Calculate statistics
            if pnl > 0:
                perf.long_gross_profit += pnl
                perf.win_long += 1
            else:
                perf.long_gross_loss -= pnl
                perf.loss_long += 1
            # Append to history list
            perf.pnl_history.append(pnl)

        elif o['side'] == 'sell' and position_type == 'short':
            # Calculate total value
            total = entry_price * short_amount + o['amount'] * o['price']
            # Increase amount
            short_amount += o['amount']
            # Liquidate entry price
            entry_price = total / short_amount
        elif o['side'] == 'buy' and position_type == 'short':
            if short_amount > o['amount']:
                # Close short partially
                pnl = (entry_price - o['price']) * o['amount']
                short_amount -= o['amount']
            elif short_amount == o['amount']:
                # Close short totally
                pnl = (entry_price - o['price']) * short_amount
                short_amount = 0
                position_type = None
            else:
                # Close short totally and open long
                pnl = (entry_price - o['price']) * short_amount
                short_amount = 0
                long_amount = o['amount'] - short_amount
                position_type = 'long'
            # Calculate statistics
            if pnl > 0:
                perf.short_gross_profit += pnl
                perf.win_short += 1
            else:
                perf.short_gross_loss -= pnl
                perf.loss_short += 1
            # Append to history list
            perf.pnl_history.append(pnl)
        long_amount = round(long_amount, precision)
        short_amount = round(short_amount, precision)

    # Cumulative PnL History
    if len(perf.pnl_history) > 1:
        c = perf.pnl_history[0]
        for i in range(1, len(perf.pnl_history)):
            c += perf.pnl_history[i]
            perf.cum_pnl_history.append(c)

    # Total
    perf.gross_profit = perf.long_gross_profit + perf.short_gross_profit
    perf.gross_loss = perf.long_gross_loss + perf.short_gross_loss
    perf.long_pnl = perf.long_gross_profit - perf.long_gross_loss
    perf.short_pnl = perf.short_gross_profit - perf.short_gross_loss
    perf.pnl = perf.long_pnl + perf.short_pnl
    perf.win = perf.win_long + perf.win_short
    perf.loss = perf.loss_long + perf.loss_short

    perf.pnl_max = max(perf.pnl_history)
    perf.pnl_min = min(perf.pnl_history)
    perf.cum_pnl_max = max(perf.cum_pnl_history)
    perf.cum_pnl_min = min(perf.cum_pnl_history)

    return perf
