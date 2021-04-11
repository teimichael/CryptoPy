# CryptoPy

A preliminary but usable quantitative trading platform for cryptocurrency.

## Disclaimer

This software is for educational purposes only and is still under development. Do not risk money which you are afraid to
lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING
RESULTS.

## Current Features

- [x] **Based on Python 3.7+**
- [x] **Binance / OKEx API Integration**
- [x] **Spot / Perpetual**
- [x] **Data Collection** (Binance only)
- [ ] **Backtesting with GUI**
- [x] **Real-Time Emulation**
- [ ] **Real trading**
- [x] **Common Indicator Support**: EMA, MACD, Bollinger Bands, etc.
- [x] **Full OHLCV-based Strategy Support**: portable strategy and seamlessly compatible among backtesting, emulation,
  and real trading.
- [x] **Bunch of Demo Strategies (Vegas Tunnel, Bollinger Bands, Momentum, ...)**

## Set Up

One-click environment setup for Ubuntu (tested on Ubuntu 20.04.2 LTS)

### Set up the running environment locally

```
chmod u+x setup/setup.sh && sudo ./setup/setup.sh local
```

or

```
chmod u+x setup.sh
.setup_local.sh
```

or

using commands in *setup_local.sh* manually.

### Set up the running environment in a Docker image

```
chmod u+x setup/setup.sh && sudo ./setup/setup.sh image
```

## Data Collector

> - backtest_config.json -> 'data': configuration file
> - data_collector.py: entry point

Collect OHLCV records from Binance.

### Configuration

- **output_dir**: output directory
- **base**: base currency
- **quote**: quote currency
- **exchange_type**: spot, future
- **quarterly**: quarterly futures (e.g. 210625)
- **interval**: K-line interval
- **start_time**: start time
- **end_time**: end time

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

> - VTCompLongIndicator.py: indicators for Vegas Tunnel Compound Long Strategy
> - VTCompLong.py: Vegas Tunnel Compound Long Strategy

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

### Configuration

- **strategy**: name of strategy
- **example**: whether the strategy is a demo
- **start_time**: start time of backtesting
- **end_time**: end time of backtesting
- **interval**: frequency of strategy execution
- **balance**: initial balance
- **pair**: pair for computing *Buy & Hold*
- **taker_fee**: taker fee
- **maker_fee**: maker fee
- **data_dir**: directory of historical data
- **result_dir**: directory of backtesting performance
- **plot**: plot indicators on visualized backtesting results
- **data**: configuration for data collector

Notice that *start_date* and *end_date* are set with local timezone.

## Real-Time Emulation

> - config.json: configuration file
> - emulate.py: entry script

Emulate real trading in real time. It needs to access to your trading account to fetch information, but it will not make
or cancel any orders.

### Configuration

- **exchange_market**: binance (default), okex
- **api_access**: Replace *YOUR_API_KEY* and *YOUR_SECRET* with your api key and secret key. If you do not have a pair,
  please refer
  to [How to create API key in Binance](https://www.binance.com/en/support/faq/360002502072-How-to-create-API)
  or [How to create API key in OKEx](https://www.okex.com/docs/en/).
- **exchange_type**: spot, future (Binance Perpetual), swap (OKEx Perpetual)
- **logs_dir**: logging directory
- **runtime_dir**: runtime file directory

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

### Running in Docker

```
docker run <-it | -d> [--env http_proxy=*] [--env https_proxy=*] [-v *:*] cryptopy <data_collector.py | backtesting.py | emulate.py | real_trading.py>
```

Use the `env` flag to set network proxy if needed. Use the `v` flag to mount the config files into containers.

Example

```
docker run -d -v /opt/logs:/project/logs -v /opt/runtime:/project/runtime cryptopy emulate.py
```

## Reference

- https://github.com/ccxt/ccxt
- https://mrjbq7.github.io/ta-lib/
- https://binance-docs.github.io/apidocs/futures/en/#change-log
- https://github.com/liihuu/KLineChart