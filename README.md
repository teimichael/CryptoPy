# CryptoPy

A preliminary but usable quantitative trading platform for cryptocurrency.

## Disclaimer

This software is for educational purposes only and is still under development. Do not risk money which you are afraid to
lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING
RESULTS.

## Current Features

- [x] **Based on Python 3.7+**
- [x] **Binance API Integration**
- [x] **Spot / Futures**
- [x] **Data Collection** (Binance)
- [ ] **Backtesting**
- [x] **Real-Time Emulation** (Binance)
- [ ] **Real trading** (Binance)
- [x] **Common Indicator Support**: EMA, MACD, Bollinger Bands, etc.
- [x] **Full OHLCV-based Strategy Support**: portable strategy and seamlessly compatible among backtesting, emulation,
  and real trading.
- [x] **Demo Vegas Tunnel Strategy**

## Data Collector

> - backtest_config.json -> 'data': configuration file
> - data_collector.py: entry point

Collect OHLCV records from Binance. Notice that *start_date* and *end_date* are set with UTC.

For more information, please refer to [binance_data](https://github.com/uneasyguy/binance_data).

### Dependency

[binance-data](https://pypi.org/project/binance-data/0.1.6/)

## Strategy

> strategy/*.py

Write your strategy here.

> strategy/indicator/*.py

Write your indicators here.

### Demo

- Vegas Tunnel Classic Strategy

> - VTClassic.py: indicators for Vegas Tunnel Classic Strategy
> - VTLClassicIndicator: Vegas Tunnel Classic Strategy (long only)

- Vegas Tunnel Compound Long Strategy

> - VTLCompIndicator.py: indicators for Vegas Tunnel Compound Long Strategy
> - VTLCompound.py: Vegas Tunnel Compound Strategy

- Bollinger Bands Classic Strategy

> - BBClassicIndicator.py: indicators for Bollinger Bands Classic Strategy
> - BBClassic.py: Bollinger Bands Classic Strategy (long)

- Bollinger Bands Compound Strategy

> - BBCompIndicator.py: indicators for Bollinger Bands Compound Strategy
> - BBCompound.py: Bollinger Bands Compound Strategy (long)

- Momentum Classic Strategy

> - MomClassicIndicator.py: indicators for Momentum Classic Strategy
> - MomClassic.py: Momentum Classic Strategy

### Dependency

[TA-Lib](https://mrjbq7.github.io/ta-lib/)

Please check the [official document](https://mrjbq7.github.io/ta-lib/install.html) to install TA-Lib.

## Backtesting

> - backtest_config.json: configuration file
> - backtesting.py: entry script

### Support time frame

- 1h
- 15m
- 5m
- 3m
- 1m

Notice that *start_date* and *end_date* are set with local timezone.

## Real-Time Emulation

> - config.json: configuration file
> - emulate.py: entry script

Emulate real trading in real time. It needs to access to your trading account to fetch information, but it will not make
or cancel any orders.

### Configuration

Replace *YOUR_API_KEY* and *YOUR_SECRET*. If you do not have the pair, please refer
to [How to create API](https://www.binance.com/en/support/faq/360002502072-How-to-create-API).

### Dependency

[ccxt](https://github.com/ccxt/ccxt)

## Real Trading

> - config.json: configuration file
> - real_trading.py: entry script

DO NOT use real trading directly without any modification and fully tested strategies. Real-trading bot has not been
fully implemented. Please know exactly what you are doing.

### Dependency

[ccxt](https://github.com/ccxt/ccxt)

## Command

### Run

```
python(3) <data_collector.py | backtesting.py | emulate.py | real_trading.py>
```

## Reference

- https://github.com/ccxt/ccxt
- https://mrjbq7.github.io/ta-lib/
- https://github.com/uneasyguy/binance_data
- https://binance-docs.github.io/apidocs/futures/en/#change-log