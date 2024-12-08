import MetaTrader5 as mt5
import json
import os
import subprocess
import math

# Define trading order constants
ORDER_BUY = 0
ORDER_SELL = 1
ORDER_BUY_STOP = 4
ORDER_SELL_STOP = 5
TRADE_ACTION_DEAL = 1

def load_settings(file_path="settings.json"):
    with open(file_path, "r") as file:
        return json.load(file)


def initialize_mt5(mt5_path):
    if not os.path.exists(mt5_path):
        raise FileNotFoundError(f"MetaTrader 5 executable not found at: {mt5_path}")

    if not mt5.initialize():
        print("MT5 is not running. Attempting to start...")
        subprocess.Popen(mt5_path)
        print(f"Starting MetaTrader 5 from: {mt5_path}")

    if not mt5.initialize():
        raise RuntimeError(f"MT5 Initialization failed: {mt5.last_error()}")
    print("MT5 Initialized successfully.")


def check_symbol(symbol):
    """
    Check if the symbol is available and activated with the broker.
    """
    if not mt5.symbol_select(symbol, True):  # Try to activate the symbol
        raise RuntimeError(f"Symbol {symbol} is not available with your broker.")
    print(f"Symbol {symbol} is available and active.")


def get_supported_filling_mode(symbol):
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        raise RuntimeError(f"Symbol {symbol} not found.")

    if symbol_info.filling_mode & mt5.ORDER_FILLING_FOK:
        return mt5.ORDER_FILLING_FOK
    elif symbol_info.filling_mode & mt5.ORDER_FILLING_IOC:
        return mt5.ORDER_FILLING_IOC
    elif symbol_info.filling_mode & mt5.ORDER_FILLING_RETURN:
        return mt5.ORDER_FILLING_RETURN
    else:
        raise RuntimeError(f"No supported filling modes for symbol {symbol}.")


def calculate_lot_sizes_correctly(current_price, take_profit_price, topup_levels, total_profit_target, risk_percent, account_size, point_value, initial_stop, symbol):
    """
    Calculate lot sizes for initial order and stop orders with correct scaling and risk allocation.
    """
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        raise RuntimeError(f"Symbol {symbol} not found.")
    volume_min = symbol_info.volume_min
    volume_max = symbol_info.volume_max

    # Initial risk for the market order
    risk_usd = account_size * (risk_percent / 100)
    initial_lot_size = risk_usd / (initial_stop * point_value)
    initial_lot_size = min(max(initial_lot_size, volume_min), volume_max)

    # Fördela återstående vinstmål proportionellt mellan stopordrar
    remaining_profit = total_profit_target - (initial_lot_size * (take_profit_price - current_price) / point_value)
    stop_lot_sizes = []
    for level in topup_levels:
        proportion = level / 100
        lot_size = (remaining_profit * proportion) / ((take_profit_price - current_price) * point_value * proportion)
        stop_lot_size = min(max(lot_size, volume_min), volume_max)
        stop_lot_sizes.append(stop_lot_size)

    return round(initial_lot_size, 2), [round(size, 2) for size in stop_lot_sizes]


def calculate_lot_sizes_correctly_v2(current_price, take_profit_price, topup_levels, total_profit_target, risk_percent, account_size, point_value, initial_stop, symbol):
    """
    Calculate lot sizes for initial order and stop orders, ensuring all match the total profit target.
    """
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        raise RuntimeError(f"Symbol {symbol} not found.")
    volume_min = symbol_info.volume_min
    volume_max = symbol_info.volume_max

    # Första orderns risk
    risk_usd = account_size * (risk_percent / 100)
    initial_lot_size = risk_usd / (initial_stop * point_value)
    initial_lot_size = min(max(initial_lot_size, volume_min), volume_max)

    # Vinst från första ordern vid TP
    profit_first_order = initial_lot_size * (take_profit_price - current_price) / point_value

    # Resterande vinstmål
    remaining_profit_target = total_profit_target - profit_first_order
    if remaining_profit_target <= 0:
        raise RuntimeError("Remaining profit target is negative or zero. Adjust your settings.")

    # Proportionellt fördela lotstorlekar för stopordrar
    stop_lot_sizes = []
    for level in topup_levels:
        proportion = level / 100
        contribution = proportion * remaining_profit_target
        pip_distance = (take_profit_price - current_price) * proportion
        lot_size = contribution / (pip_distance * point_value)
        stop_lot_sizes.append(min(max(lot_size, volume_min), volume_max))

    return round(initial_lot_size, 2), [round(size, 2) for size in stop_lot_sizes]


def calculate_topup_lots(initial_lot, topup_levels):
    topup_lots = [initial_lot]
    multiplier = 2
    for _ in topup_levels[1:]:
        topup_lots.append(topup_lots[-1] * multiplier)
    return topup_lots


def display_order_plan(symbol, initial_lot, topup_lots, stop_loss_pips, take_profit_pips):
    print("\n--- Order Plan ---")
    print(f"Symbol: {symbol}")
    print(f"Initial Lot Size: {initial_lot}")
    print(f"Top-Up Lot Sizes: {topup_lots}")
    print(f"Stop Loss (pips): {stop_loss_pips}")
    print(f"Take Profit (pips): {take_profit_pips}")
    print("------------------\n")


def confirm_order():
    """
    Confirm with the user whether to place the orders or not.
    """
    while True:
        user_input = input("Do you want to place the orders? (y/n): ").lower()
        if user_input in ["y", "n"]:
            return user_input == "y"
        print("Invalid input. Please enter 'y' for yes or 'n' for no.")


def print_symbol_info(symbol):
    """
    Print the symbol's trading specifications.
    """
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        raise RuntimeError(f"Symbol {symbol} not found.")

    print("\n--- Symbol Specifications ---")
    print(f"Symbol: {symbol}")
    print(f"Minimum Volume: {symbol_info.volume_min}")
    print(f"Maximum Volume: {symbol_info.volume_max}")
    print(f"Volume Step: {symbol_info.volume_step}")
    print(f"Point Value: {symbol_info.point}")
    print(f"Contract Size: {symbol_info.trade_contract_size}")
    print("----------------------------\n")


def place_market_order(symbol, order_type, lot_size, stop_loss_pips, take_profit_pips):
    """
    Place a market order in MetaTrader 5 with SL and TP adjusted dynamically.
    """
    # Hämta marknadspris
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        raise RuntimeError(f"Failed to get market price for {symbol}.")

    price = tick.ask if order_type == ORDER_BUY else tick.bid
    point_value = mt5.symbol_info(symbol).point

    # Sätt minsta avstånd (default 10 punkter om inget annat är tillgängligt)
    min_distance = max(getattr(mt5.symbol_info(symbol), 'trade_stops_level', 10), 10) * point_value

    # Beräkna SL och TP med minsta avstånd inkluderat
    if order_type == ORDER_BUY:
        sl_price = price - max(stop_loss_pips * point_value, min_distance)
        tp_price = price + max(take_profit_pips * point_value, min_distance)
    else:  # ORDER_SELL
        sl_price = price + max(stop_loss_pips * point_value, min_distance)
        tp_price = price - max(take_profit_pips * point_value, min_distance)

    # Skriv ut detaljer som skickas med ordern
    print("\n--- Sending Order Details ---")
    print(f"Order Type: {'BUY' if order_type == ORDER_BUY else 'SELL'}")
    print(f"Current Price: {price}")
    print(f"Lot Size: {lot_size}")
    print(f"Stop Loss Price: {sl_price}")
    print(f"Take Profit Price: {tp_price}")
    print("-----------------------------\n")

    # Validera och justera lot size
    validated_lot_size = validate_volume(symbol, lot_size)

    # Skicka order
    filling_mode = get_supported_filling_mode(symbol)
    request = {
        "action": TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": validated_lot_size,
        "type": order_type,
        "price": price,
        "sl": sl_price,
        "tp": tp_price,
        "magic": 123456,
        "comment": "Market order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_mode,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        raise RuntimeError(f"Order placement failed: {result.comment}")
    print(f"Market order placed successfully: {result}")


def print_symbol_stop_freeze_levels(symbol):
    """
    Print the symbol's stop level and freeze level.
    """
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        raise RuntimeError(f"Symbol {symbol} not found.")

    print("\n--- Symbol Stop/Freeze Levels ---")
    print(f"Stop Level (points): {symbol_info.stop_level}")
    print(f"Freeze Level (points): {symbol_info.freeze_level}")
    print("-------------------------------\n")


def place_stop_orders(symbol, order_type, entry_levels, lot_sizes, stop_loss_pips, take_profit_price):
    """
    Place multiple stop orders with individual SL, entry levels, and lot sizes.
    """
    point_value = mt5.symbol_info(symbol).point

    for i, (entry_price, lot_size) in enumerate(zip(entry_levels, lot_sizes)):
        # Beräkna SL och TP för varje stop order
        if order_type == ORDER_BUY_STOP:
            sl_price = entry_price - (stop_loss_pips * point_value)
            tp_price = take_profit_price
        elif order_type == ORDER_SELL_STOP:
            sl_price = entry_price + (stop_loss_pips * point_value)
            tp_price = take_profit_price
        else:
            raise ValueError("Invalid order type for stop orders.")

        # Validera och justera lot size
        validated_lot_size = validate_volume(symbol, lot_size)

        # Skicka stop order
        filling_mode = get_supported_filling_mode(symbol)
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": validated_lot_size,
            "type": order_type,
            "price": entry_price,
            "sl": sl_price,
            "tp": tp_price,
            "magic": 123456 + i,  # Unikt för varje stop order
            "comment": f"Stop order {i+1}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to place stop order {i+1}: {result.comment}")
        else:
            print(f"Stop order {i+1} placed successfully: {result}")


def validate_volume(symbol, volume):
    """
    Validate and adjust the volume based on the symbol's specifications.
    """
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        raise RuntimeError(f"Symbol {symbol} not found.")

    min_volume = symbol_info.volume_min  # Minimum volume
    max_volume = symbol_info.volume_max  # Maximum volume
    step_volume = symbol_info.volume_step  # Volume step

    # Ensure volume is within valid range
    if volume < min_volume:
        print(f"Volume {volume} is below the minimum for {symbol}. Adjusting to {min_volume}.")
        volume = min_volume
    elif volume > max_volume:
        print(f"Volume {volume} exceeds the maximum for {symbol}. Adjusting to {max_volume}.")
        volume = max_volume

    # Adjust volume to nearest valid step
    volume = round(volume / step_volume) * step_volume
    return round(volume, 8)  # Return rounded volume


def print_symbol_attributes(symbol):
    """
    Print all available attributes of a symbol for debugging.
    """
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        raise RuntimeError(f"Symbol {symbol} not found.")

    print("\n--- Symbol Attributes ---")
    for attr in dir(symbol_info):
        if not attr.startswith('_'):
            print(f"{attr}: {getattr(symbol_info, attr)}")
    print("------------------------\n")


def calculate_stop_order_details(current_price, take_profit_price, topup_levels, total_profit_target, point_value):
    """
    Calculate entry levels and lot sizes for stop orders.
    """
    # Beräkna avståndet mellan entry och TP
    total_distance = take_profit_price - current_price

    # Beräkna entry levels för varje topup nivå
    entry_levels = [
        current_price + (level / 100) * total_distance
        for level in topup_levels
    ]

    # Beräkna total vinst per pip
    total_pip_value = total_distance * point_value

    # Fördela lotstorlekar proportionellt för att nå målet
    lot_sizes = [
        (total_profit_target / total_pip_value) * (level / 100)
        for level in topup_levels
    ]

    return entry_levels, lot_sizes


def display_order_levels(symbol, current_price, initial_stop, take_profit_pips, topup_levels):
    """
    Display SL and TP levels for all orders.
    """
    point_value = mt5.symbol_info(symbol).point

    print("\n--- Order Levels ---")
    print(f"Current Price: {current_price}")

    # Initial order
    initial_sl = current_price - (initial_stop * point_value)
    initial_tp = current_price + (take_profit_pips * point_value)
    print(f"Initial Order -> SL: {initial_sl}, TP: {initial_tp}")

    # Top-up orders
    for i, level in enumerate(topup_levels, start=1):
        topup_price = current_price + (level * point_value)
        sl_price = topup_price - (initial_stop * point_value)
        tp_price = topup_price + (take_profit_pips * point_value)
        print(f"Top-Up {i} -> Entry: {topup_price}, SL: {sl_price}, TP: {tp_price}")

    print("---------------------\n")


def adjust_stop_loss(orders, breakeven_stop_level, current_price, point_value):
    """
    Adjust SL for all active orders to ensure break even when a new order is triggered.
    """
    total_lots = sum(order['lot_size'] for order in orders)
    weighted_price = sum(order['entry_price'] * order['lot_size'] for order in orders) / total_lots

    # Flytta SL för att säkra "break even" på gruppnivå
    new_sl = weighted_price + (breakeven_stop_level * point_value)
    for order in orders:
        order['sl'] = new_sl
        print(f"Adjusting SL for order {order['id']} to {new_sl}")


def handle_orders(market_order, stop_orders, breakeven_stop_level, current_price, point_value):
    """
    Handle active orders and adjust SL dynamically when new orders are triggered.
    """
    active_orders = [market_order]
    for stop_order in stop_orders:
        if stop_order['entry_price'] <= current_price:
            # Aktivera stoporder
            print(f"Activating stop order {stop_order['id']}")
            stop_order['active'] = True
            active_orders.append(stop_order)

            # Justera SL för alla aktiva ordrar
            adjust_stop_loss(active_orders, breakeven_stop_level, current_price, point_value)


def validate_total_profit(lot_sizes, current_price, take_profit_price, account_size, target_gain_percent, point_value):
    """
    Validate that the total profit from all orders equals the target gain.
    """
    # Målvinst i pengar
    target_profit = account_size * (target_gain_percent / 100)

    # Beräkna faktisk vinst från alla ordrar
    total_profit = 0
    for lot_size in lot_sizes:
        pip_distance = (take_profit_price - current_price) / point_value
        total_profit += lot_size * pip_distance * point_value

    # Kontrollera om den totala vinsten matchar målet
    return abs(total_profit - target_profit) < 1e-2  # Tolerans på 0.01 för avrundningsfel


def calculate_lot_sizes_with_validation(current_price, take_profit_price, topup_levels, total_profit_target, risk_percent, account_size, point_value, initial_stop, symbol, target_gain_percent):
    """
    Calculate lot sizes iteratively to ensure total profit matches the target and respects volume limits.
    """
    max_iterations = 10  # Max antal omberäkningar
    iteration = 0

    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        raise RuntimeError(f"Symbol {symbol} not found.")
    volume_max = symbol_info.volume_max

    while iteration < max_iterations:
        # Beräkna lot sizes
        initial_lot_size, stop_lot_sizes = calculate_lot_sizes_correctly(
            current_price, take_profit_price, topup_levels, total_profit_target, risk_percent, account_size, point_value, initial_stop, symbol
        )

        # Logga detaljer om beräkningen
        print(f"Iteration {iteration + 1}:")
        print(f"  Initial Lot Size: {initial_lot_size}")
        print(f"  Stop Lot Sizes: {stop_lot_sizes}")
        print(f"  Total Profit Target: {total_profit_target}")

        # Validera total vinst
        all_lot_sizes = [initial_lot_size] + stop_lot_sizes
        is_valid = validate_total_profit(all_lot_sizes, current_price, take_profit_price, account_size, target_gain_percent, point_value)

        if is_valid:
            return initial_lot_size, stop_lot_sizes  # Returnera om allt är korrekt

        # Justera vinstmål för att iterera
        iteration += 1
        total_profit_target *= 0.99  # Justera något nedåt vid misslyckande

    raise RuntimeError("Failed to calculate valid lot sizes after multiple iterations.")


def scale_lot_sizes(lot_sizes, volume_max):
    """
    Scale down lot sizes proportionally if any lot size exceeds the maximum allowed volume.
    """
    if all(lot <= volume_max for lot in lot_sizes):
        return lot_sizes  # Inga justeringar behövs

    # Skala ner proportionellt baserat på den största volymen
    max_lot = max(lot_sizes)
    scaling_factor = volume_max / max_lot

    return [round(lot * scaling_factor, 2) for lot in lot_sizes]


def display_debugging_table(lot_sizes, current_price, take_profit_price, initial_stop, point_value, account_size, target_gain_percent):
    """
    Display a table showing lot sizes, SL loss, TP profit, and validate total profit.
    """
    target_profit = account_size * (target_gain_percent / 100)
    table_data = []
    total_profit = 0
    total_loss = 0

    for i, lot_size in enumerate(lot_sizes, start=1):
        pip_distance_tp = (take_profit_price - current_price) / point_value
        pip_distance_sl = initial_stop
        profit_per_pip = lot_size * point_value

        # Beräkna vinst och förlust
        profit = profit_per_pip * pip_distance_tp
        loss = profit_per_pip * pip_distance_sl

        total_profit += profit
        total_loss += loss

        table_data.append({
            "Order": f"Order {i}",
            "Lot Size": round(lot_size, 2),
            "Profit (TP)": round(profit, 2),
            "Loss (SL)": round(loss, 2)
        })

    # Visa tabellen
    import pandas as pd
    df = pd.DataFrame(table_data)
    print("\n--- Debugging Table ---")
    print(df)
    print(f"\nTarget Profit: {target_profit}")
    print(f"Calculated Total Profit (TP): {round(total_profit, 2)}")
    print(f"Calculated Total Loss (SL): {round(total_loss, 2)}")
    print("-----------------------\n")

    # Kontrollera om värdena matchar målet
    if abs(total_profit - target_profit) > 1e-2:
        print("WARNING: Calculated total profit does not match target profit.")
        return False
    return True


def calculate_lot_sizes_with_scaling(current_price, take_profit_price, topup_levels, total_profit_target, risk_percent, account_size, point_value, initial_stop, symbol, target_gain_percent):
    """
    Calculate lot sizes with scaling to ensure they stay within volume limits and meet profit targets.
    """
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        raise RuntimeError(f"Symbol {symbol} not found.")
    volume_min = symbol_info.volume_min
    volume_max = symbol_info.volume_max

    # Initial risk for the market order
    initial_risk = account_size * (risk_percent / 100)
    total_distance = take_profit_price - current_price

    # Beräkna initial lot size
    initial_lot_size = initial_risk / (initial_stop * point_value)
    initial_lot_size = min(max(initial_lot_size, volume_min), volume_max)  # Begränsa till min och max

    # Fördela vinsten mellan stopordrar proportionellt
    stop_lot_sizes = []
    for level in topup_levels:
        proportion = level / 100
        contribution = proportion * total_profit_target
        pip_distance = total_distance * proportion
        lot_size = contribution / (pip_distance * point_value)
        stop_lot_sizes.append(lot_size)

    # Skala lotstorlekar om de överstiger maxvolym
    max_lot = max([initial_lot_size] + stop_lot_sizes)
    if max_lot > volume_max:
        scaling_factor = volume_max / max_lot
        initial_lot_size *= scaling_factor
        stop_lot_sizes = [lot * scaling_factor for lot in stop_lot_sizes]

    # Begränsa till min och max
    initial_lot_size = round(min(max(initial_lot_size, volume_min), volume_max), 2)
    stop_lot_sizes = [round(min(max(lot, volume_min), volume_max), 2) for lot in stop_lot_sizes]

    return initial_lot_size, stop_lot_sizes


def calculate_lot_sizes_for_currency_pair(current_price, take_profit_price, topup_levels, total_profit_target, risk_percent, account_size, initial_stop, symbol):
    """
    Calculate lot sizes and pip-based gains for a standard forex pair like GBPJPY.
    """
    # Hämta symbolinfo
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        raise RuntimeError(f"Symbol {symbol} not found.")
    point_value = symbol_info.point
    contract_size = symbol_info.trade_contract_size
    volume_min = symbol_info.volume_min
    volume_max = symbol_info.volume_max

    # Initial risk för marknadsordern
    risk_usd = account_size * (risk_percent / 100)
    initial_lot_size = risk_usd / (initial_stop * point_value * contract_size)
    initial_lot_size = min(max(initial_lot_size, volume_min), volume_max)

    # Vinst från initialorder vid TP
    profit_initial_order = initial_lot_size * (take_profit_price - current_price) / point_value

    # Skala initial lot size om den inte når rimliga nivåer
    if profit_initial_order < total_profit_target * 0.1:  # Mindre än 10% av målet
        scaling_factor = (total_profit_target * 0.1) / profit_initial_order
        initial_lot_size *= scaling_factor
        profit_initial_order = total_profit_target * 0.1

    # Resterande vinstmål
    remaining_profit_target = total_profit_target - profit_initial_order
    if remaining_profit_target <= 0:
        raise RuntimeError("Remaining profit target is negative or zero. Adjust your settings.")

    # Proportionellt fördela stopordrars lots
    stop_lot_sizes = []
    pip_gains = []
    for level in topup_levels:
        proportion = level / 100
        contribution = proportion * remaining_profit_target
        pip_distance = (take_profit_price - current_price) * proportion
        lot_size = contribution / (pip_distance * point_value * contract_size)
        lot_size = min(max(lot_size, volume_min), volume_max)
        stop_lot_sizes.append(round(lot_size, 2))
        pip_gains.append(round(lot_size * pip_distance, 2))  # Vinst i pips för varje order

    return round(initial_lot_size, 2), stop_lot_sizes, pip_gains


def adjust_tp_sl_for_symbol(symbol, tp_points, sl_points):
    """
    Adjust TP and SL points based on the symbol's precision.
    """
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        raise RuntimeError(f"Symbol {symbol} not found.")

    # Justera TP och SL för symbolens precision
    digits = symbol_info.digits
    factor = 10 ** (digits - 2)  # Anpassa för skillnader i decimaler (t.ex. BTCUSD vs GBPJPY)

    tp_adjusted = tp_points / factor
    sl_adjusted = sl_points / factor
    return tp_adjusted, sl_adjusted


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

    symbol = "GBPJPY"  # Anpassa symbol vid behov

    # Initiera MT5
    initialize_mt5(mt5_path)

    # Kontrollera att symbolen är aktiv
    check_symbol(symbol)

    # Hämta dynamisk symbolinformation
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        raise RuntimeError(f"Symbol {symbol} not found.")
    point_value = symbol_info.point
    contract_size = symbol_info.trade_contract_size

    # Hämta aktuellt pris
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        raise RuntimeError(f"Failed to get market price for {symbol}.")
    current_price = tick.ask  # Vi antar köporder

    # Anpassa TP och SL för symbolens precision
    tp_points, sl_points = adjust_tp_sl_for_symbol(symbol, pips, initial_stop)

    # Beräkna TP och SL i prisnivåer
    take_profit_price = current_price + (tp_points * point_value)

    # Definiera totalvinstmålet
    total_profit_target = account_size * (target_gain_percent / 100)

    # Försök beräkna lotstorlekar och pip-gains
    try:
        initial_lot_size, stop_lot_sizes, pip_gains = calculate_lot_sizes_for_currency_pair(
            current_price, take_profit_price, topup_levels, total_profit_target, risk_percent, account_size, sl_points, symbol
        )
    except RuntimeError as e:
        print(f"Error: {e}")
        return

    # Skapa och visa debugging-tabellen
    lot_sizes = [initial_lot_size] + stop_lot_sizes
    table_data = []
    total_gain = 0

    for i, (level, lot_size, pip_gain) in enumerate(zip(
        [0] + topup_levels,
        lot_sizes,
        [round(initial_lot_size * (take_profit_price - current_price) / point_value, 2)] + pip_gains
    )):
        pip_distance = (take_profit_price - current_price) * (level / 100) if i > 0 else (take_profit_price - current_price)
        table_data.append({
            "Order": "Initial" if i == 0 else f"Topup{i}",
            "Level (%)": level,
            "Pips": round(pip_distance / point_value, 2),
            "Lot Size": lot_size,
            "Pip Gain": pip_gain,
            "Gain in $": round(pip_gain * point_value, 2)
        })
        total_gain += pip_gain

    import pandas as pd
    df = pd.DataFrame(table_data)
    print("\n--- Trade Plan ---")
    print(df)
    print(f"\nTotal Gain: ${round(total_gain, 2)}")
    print("------------------\n")

    # Bekräfta innan orderläggning
    if not confirm_order():
        print("Order placement cancelled.")
        return

    # Lägg marknadsorder
    place_market_order(symbol, ORDER_BUY, initial_lot_size, sl_points, pips)

    # Lägg stopordrar
    entry_levels = [
        current_price + (level / 100) * (take_profit_price - current_price)
        for level in topup_levels
    ]
    place_stop_orders(symbol, ORDER_BUY_STOP, entry_levels, stop_lot_sizes, sl_points, take_profit_price)

    print("All orders placed successfully.")


if __name__ == "__main__":
    main()
