# CryptoPy

A preliminary but usable quantitative trading platform for cryptocurrency.

## Disclaimer

This software is for educational purposes only and is still under development. Do not risk money which you are afraid to
lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING
RESULTS.

## Current Features

- [x] **Based on Python 3.7+**
- [x] **Binance API Integration**
- [x] **Data Collection** (Binance)
- [ ] **Backtesting**
- [x] **Real-Time Emulation** (Binance)
- [ ] **Real trading** (Binance)
- [x] **Common Indicator Support**: EMA, MACD, Bollinger Bands, etc.
- [x] **Full OHLCV-based Strategy Support**: portable strategy and seamlessly compatible among backtesting, emulation,
  and real trading.
- [x] **Demo Vegas Tunnel Strategy**

## Data Collector

> data_collector.py

Collect OHLCV records from Binance. For more information, please refer
to [binance_data](https://github.com/uneasyguy/binance_data).

### Dependency

[binance-data 0.1.6](https://pypi.org/project/binance-data/0.1.6/)

## Strategy

> strategy/*.py

Write your strategy here.

### Demo

> - Indicator.py: indicators for Vegas Tunnel
> - VegasTunnel.py: Vegas Tunnel Strategy (long only)

### Dependency

[TA-Lib](https://mrjbq7.github.io/ta-lib/)

## Backtesting

> - backtest_config.json: configuration file
> - backtesting.py: entry script

Currently support *1h* and *15m*.

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