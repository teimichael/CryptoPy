from core.model import PerfInfo

precision = 10


# TODO funding, fee, rate, etc.
def get_performance(orders, taker_fee: float, maker_fee: float) -> PerfInfo:
    perf = PerfInfo()
    if len(orders) < 1:
        return perf

    # Classify orders by symbol
    order_s = {}
    for o in orders:
        symbol = o['symbol']
        if symbol not in order_s.keys():
            order_s[symbol] = []
        order_s[symbol].append(o)

    # Calculate performance by symbol
    perfs = []
    for os in order_s.values():
        perfs.append(get_symbol_perf(os, taker_fee, maker_fee))

    # Calculate total performance
    pnl_history = {}
    for p in perfs:
        for pnl in p.pnl_history:
            if pnl[0] not in pnl_history.keys():
                pnl_history[pnl[0]] = 0
            pnl_history[pnl[0]] += pnl[1]

        perf.pnl += p.pnl
        perf.long_pnl += p.long_pnl
        perf.short_pnl += p.short_pnl
        perf.gross_profit += p.gross_profit
        perf.long_gross_profit += p.long_gross_profit
        perf.short_gross_profit += p.short_gross_profit
        perf.gross_loss += p.gross_loss
        perf.long_gross_loss += p.long_gross_loss
        perf.short_gross_loss += p.short_gross_loss
        perf.win += p.win
        perf.win_long += p.win_long
        perf.win_short += p.win_short
        perf.loss += p.loss
        perf.loss_long += p.loss_long
        perf.loss_short += p.loss_short
        perf.commission_paid += p.commission_paid

    perf.percent_profitable = perf.win / (perf.win + perf.loss) if perf.win > 0 else 0

    for i in sorted(pnl_history.keys()):
        perf.pnl_history.append([i, pnl_history[i]])

    if len(perf.pnl_history) > 0:
        c = 0
        for i in range(0, len(perf.pnl_history)):
            c += perf.pnl_history[i][1]
            perf.cum_pnl_history.append([perf.pnl_history[i][0], c])

    pnl_h = [r[1] for r in perf.pnl_history]
    pnl_cum_h = [r[1] for r in perf.cum_pnl_history]
    perf.pnl_max = max(pnl_h) if len(pnl_h) > 0 else 0
    perf.pnl_min = min(pnl_h) if len(pnl_h) > 0 else 0
    perf.cum_pnl_max = max(pnl_cum_h) if len(pnl_cum_h) > 0 else 0
    perf.cum_pnl_min = min(pnl_cum_h) if len(pnl_cum_h) > 0 else 0

    return perf


# Get performance for orders with the same symbol
def get_symbol_perf(orders, taker_fee: float, maker_fee: float) -> PerfInfo:
    perf = PerfInfo()

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

        # Calculate paid commission
        fee = taker_fee if o['type'] == 'market' else maker_fee / 100
        perf.commission_paid += o['price'] * o['amount'] * fee

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
            perf.pnl_history.append([o['timestamp'], pnl])

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
            perf.pnl_history.append([o['timestamp'], pnl])
        long_amount = round(long_amount, precision)
        short_amount = round(short_amount, precision)

    # Cumulative PnL History
    if len(perf.pnl_history) > 0:
        c = 0
        for i in range(0, len(perf.pnl_history)):
            c += perf.pnl_history[i][1]
            perf.cum_pnl_history.append([perf.pnl_history[i][0], c])

    # Total
    perf.gross_profit = perf.long_gross_profit + perf.short_gross_profit
    perf.gross_loss = perf.long_gross_loss + perf.short_gross_loss
    perf.long_pnl = perf.long_gross_profit - perf.long_gross_loss
    perf.short_pnl = perf.short_gross_profit - perf.short_gross_loss
    perf.pnl = perf.long_pnl + perf.short_pnl
    perf.win = perf.win_long + perf.win_short
    perf.loss = perf.loss_long + perf.loss_short
    perf.percent_profitable = perf.win / (perf.win + perf.loss) if perf.win > 0 else 0

    pnl_h = [r[1] for r in perf.pnl_history]
    pnl_cum_h = [r[1] for r in perf.cum_pnl_history]

    perf.pnl_max = max(pnl_h) if len(pnl_h) > 0 else 0
    perf.pnl_min = min(pnl_h) if len(pnl_h) > 0 else 0
    perf.cum_pnl_max = max(pnl_cum_h) if len(pnl_cum_h) > 0 else 0
    perf.cum_pnl_min = min(pnl_cum_h) if len(pnl_cum_h) > 0 else 0

    return perf
