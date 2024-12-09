import MetaTrader5 as mt5
import json
import math


# Ladda inställningar
def load_settings():
    with open('settings.json', 'r') as file:
        return json.load(file)


# Initiera MT5
def initialize_mt5(mt5_path):
    if not mt5.initialize(mt5_path):
        raise RuntimeError("Failed to initialize MetaTrader 5")


# Kontrollera att symbolen är aktiv
def check_symbol(symbol):
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"Failed to select symbol {symbol}")


# Validera volym
def validate_volume(symbol, lot_size):
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        raise RuntimeError(f"Symbol {symbol} not found.")

    min_lot = symbol_info.volume_min
    max_lot = symbol_info.volume_max
    lot_step = symbol_info.volume_step

    valid_lot_size = max(min_lot, min(lot_size, max_lot))
    valid_lot_size = math.floor(valid_lot_size / lot_step) * lot_step
    return valid_lot_size


# Placera marknadsorder
def place_market_order(symbol, order_type, volume, sl_points, tp_points):
    price = mt5.symbol_info_tick(symbol).ask
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": price - sl_points * mt5.symbol_info(symbol).point,
        "tp": price + tp_points * mt5.symbol_info(symbol).point,
        "magic": 234000,
        "comment": "Market order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        raise RuntimeError(f"Order failed: {result.comment}")
    return result


# Placera stop order
def place_stop_order(symbol, order_type, entry_price, volume, sl_points, tp_price):
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": entry_price,
        "sl": entry_price - sl_points * mt5.symbol_info(symbol).point,
        "tp": tp_price,
        "magic": 234000,
        "comment": "Stop order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        raise RuntimeError(f"Order failed: {result.comment}")
    return result


# Huvudfunktion
def main():
    # Ladda inställningar
    settings = load_settings()

    mt5_path = settings["mt5_path"]
    account_size = settings["account_size"]
    target_gain_percent = settings["target_gain_percent"]
    initial_stop = settings["initial_stop"]
    risk_percent = settings["risk_percent"]
    topup_levels = settings["topup_levels"]
    pips = settings["pips"]
    symbol = "GBPJPY"  # Definiera symbol här

    # Initiera MT5
    initialize_mt5(mt5_path)

    # Kontrollera att symbolen är aktiv
    check_symbol(symbol)

    # Hämta symbolinformation
    symbol_info = mt5.symbol_info(symbol)
    point_value = symbol_info.point
    contract_size = symbol_info.trade_contract_size
    pip_value = point_value * contract_size

    # Hämta aktuellt pris
    tick = mt5.symbol_info_tick(symbol)
    current_price = tick.ask

    # Anpassa TP och SL för symbolens precision
    tp_points, sl_points = pips, initial_stop

    # Beräkna TP och SL i prisnivåer
    take_profit_price = current_price + (tp_points * point_value)

    # Beräkna marknadsorder
    initial_lot_size = validate_volume(symbol, account_size * (risk_percent / 100) / sl_points)

    # Placera marknadsorder
    place_market_order(symbol, mt5.ORDER_TYPE_BUY, initial_lot_size, sl_points, tp_points)

    # Lägg stopordrar
    entry_level = current_price + (topup_levels[0] / 100) * (take_profit_price - current_price)
    place_stop_order(symbol, mt5.ORDER_TYPE_BUY_STOP, entry_level, initial_lot_size, sl_points, take_profit_price)


if __name__ == "__main__":
    main()
