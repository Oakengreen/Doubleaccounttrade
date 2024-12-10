import MetaTrader5 as mt5
import logging

# Konfigurera loggning
logging.basicConfig(
    filename="order_execution.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def points_per_pip(symbol):
    """
    Beräknar hur många points som motsvarar en pip för en given symbol.
    :param symbol: Symbolens namn.
    :return: Points per pip.
    """
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        print(f"Failed to retrieve symbol info for {symbol}.")
        return None

    # Beräkna points per pip
    return 1 / symbol_info.point

def place_order(symbol, lot_size, order_type, price=None, stop_loss_pips=None, take_profit_pips=None):
    """
    Lägger en order på MetaTrader 5-plattformen med specifika SL och TP.
    """
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol {symbol}. Exiting.")
        logging.error(f"Failed to select symbol {symbol}.")
        return None

    # Hämta symbolinformation och tickdata
    symbol_info = mt5.symbol_info(symbol)
    tick = mt5.symbol_info_tick(symbol)
    if not symbol_info or not tick:
        print(f"Failed to retrieve symbol info or tick data for {symbol}.")
        return None

    # Beräkna points per pip
    points_per_pip_value = points_per_pip(symbol)
    if points_per_pip_value is None:
        print(f"Failed to calculate points per pip for {symbol}.")
        return None

    # Om `price` är None, sätt standardpris
    price = price or (tick.ask if order_type in ['BUY', 'BUY_STOP'] else tick.bid)

    # Konvertera SL och TP från pips till prisnivåer
    point = symbol_info.point

    # Justera prisnivåer baserat på ordertyp
    if order_type in ['BUY', 'BUY_STOP']:
        sl = price - stop_loss_pips * point * points_per_pip_value if stop_loss_pips else None
        tp = price + take_profit_pips * point * points_per_pip_value if take_profit_pips else None
    elif order_type in ['SELL', 'SELL_STOP']:
        sl = price + stop_loss_pips * point * points_per_pip_value if stop_loss_pips else None
        tp = price - take_profit_pips * point * points_per_pip_value if take_profit_pips else None

    # Kontrollera pris för pending orders
    if order_type in ['BUY_STOP', 'SELL_STOP']:
        if order_type == 'BUY_STOP' and price <= tick.ask:
            print(f"Invalid price for BUY_STOP: {price}. Must be above current ASK.")
            return
        elif order_type == 'SELL_STOP' and price >= tick.bid:
            print(f"Invalid price for SELL_STOP: {price}. Must be below current BID.")
            return

    # Skapa orderbegäran
    request = {
        "action": mt5.TRADE_ACTION_DEAL if order_type in ['BUY', 'SELL'] else mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_BUY if order_type == 'BUY' else mt5.ORDER_TYPE_SELL if order_type == 'SELL' else mt5.ORDER_TYPE_BUY_STOP if order_type == 'BUY_STOP' else mt5.ORDER_TYPE_SELL_STOP,
        "price": round(price, symbol_info.digits),
        "sl": round(sl, symbol_info.digits) if sl else None,
        "tp": round(tp, symbol_info.digits) if tp else None,
        "deviation": 10,
        "magic": 0,
        "comment": "DA",
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    print("Order Request:", request)

    # Skicka order
    result = mt5.order_send(request)
    if result is None:
        print("Order Send Failed:", mt5.last_error())
        logging.error(f"Order Send Failed: {mt5.last_error()}")
        return None

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        logging.info(f"Order utförd: {result}")
        print(f"Order utförd: {result}")
    else:
        logging.error(f"Order misslyckades: {result}")
        print(f"Order misslyckades: {result}")

    return result

def adjust_volume(volume, symbol):
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        print(f"Failed to retrieve symbol info for {symbol}.")
        return None

    min_volume = symbol_info.volume_min
    max_volume = symbol_info.volume_max
    volume_step = symbol_info.volume_step

    # Kontrollera och justera volymen
    if volume < min_volume:
        volume = min_volume
    elif volume > max_volume:
        volume = max_volume

    # Anpassa till närmaste volymsteg
    volume = round(volume / volume_step) * volume_step
    return volume

def confirm_execution():
    """
    Frågar användaren om de vill gå vidare med att lägga ordrar.
    :return: True om användaren bekräftar, annars False.
    """
    while True:
        answer = input("Vill du lägga order? (Y/n) [Y]: ").strip().lower()
        if answer in ['', 'y', 'yes']:
            return True
        elif answer in ['n', 'no']:
            return False
        else:
            print("Ogiltigt svar. Skriv 'Y' för ja eller 'n' för nej.")
