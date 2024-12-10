import MetaTrader5 as mt5
import logging
import time

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

    # Kontrollera om symbolens punktstorlek motsvarar en pip
    if symbol_info.digits == 5 or symbol_info.digits == 3:  # Exempel: EURUSD, GBPJPY
        return 10  # En pip = 10 points
    elif symbol_info.digits == 2 or symbol_info.digits == 4:  # Exempel: USDJPY
        return 1  # En pip = 1 point
    else:
        print(f"Unexpected digit format for {symbol}. Defaulting to 1.")
        return 1

def place_order(symbol, lot_size, order_type, price=None, sl=None, tp=None):
    """
    Lägg en order på MetaTrader 5-plattformen med valfria SL och TP.
    """
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol {symbol}. Exiting.")
        return None

    request = {
        "action": mt5.TRADE_ACTION_DEAL if order_type in ['BUY', 'SELL'] else mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_BUY if order_type == 'BUY' else mt5.ORDER_TYPE_SELL if order_type == 'SELL'
        else mt5.ORDER_TYPE_BUY_STOP if order_type == 'BUY_STOP' else mt5.ORDER_TYPE_SELL_STOP,
        "price": price,
        "tp": tp,
        "deviation": 10,
        "magic": 0,
        "comment": "DA",
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Lägg endast till 'sl' om det är satt
    if sl is not None:
        request["sl"] = sl

    print("Order Request:", request)  # Debugga begäran

    # Skicka ordern
    result = mt5.order_send(request)
    if result is None:
        print("Order Send Failed:", mt5.last_error())
        return None

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"Order utförd: {result}")
    else:
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

def calculate_sl_price(entry_price, sl_pips, order_type, point, points_per_pip_value):
    """
    Beräknar giltigt Stop Loss-pris.
    """
    sl_price = None
    if order_type == 'BUY':
        sl_price = entry_price - sl_pips * point * points_per_pip_value
    elif order_type == 'SELL':
        sl_price = entry_price + sl_pips * point * points_per_pip_value

    if sl_price and sl_price < 0:
        print(f"Invalid SL price calculated: {sl_price}.")
        return None

    return round(sl_price, 5)

def calculate_tp_price(entry_price, tp_pips, order_type, point, points_per_pip_value):
    """
    Beräknar giltigt Take Profit-pris.
    """
    tp_price = None
    if order_type == 'BUY':
        tp_price = entry_price + tp_pips * point * points_per_pip_value
    elif order_type == 'SELL':
        tp_price = entry_price - tp_pips * point * points_per_pip_value

    if tp_price and tp_price < 0:
        print(f"Invalid TP price calculated: {tp_price}.")
        return None

    return round(tp_price, 5)

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

def monitor_positions(symbol, entry_price, break_even_price, levels, point, points_per_pip_value):
    """
    Övervaka positioner och uppdatera SL till break-even när stop-orders aktiveras.
    """
    print("Startar övervakning...")
    while True:
        positions = mt5.positions_get(symbol=symbol)
        if positions is None:
            print(f"Failed to get positions for {symbol}. Retrying...")
            continue

        # Kontrollera aktiva ordrar
        active_positions = [pos for pos in positions if pos.symbol == symbol]
        if not active_positions:
            print("Inga aktiva positioner. Avslutar övervakning.")
            break

        # Kontrollera om en ny stop-order har aktiverats
        for pos in active_positions:
            if pos.price_open > entry_price and pos.sl == 0:
                # Uppdatera SL för alla positioner till break-even
                new_sl = break_even_price
                for position in active_positions:
                    update_sl(position.ticket, new_sl, point, points_per_pip_value)
                print(f"Uppdaterade SL till {new_sl} för alla aktiva positioner.")
                break

        # Vänta innan nästa kontroll
        time.sleep(1)

def update_sl(ticket, sl_price, point, points_per_pip_value):
    """
    Uppdaterar SL för en given position.
    """
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "symbol": mt5.symbol_info(ticket).symbol,
        "position": ticket,
        "sl": sl_price,
        "tp": None,  # TP påverkas inte
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Misslyckades att uppdatera SL för ticket {ticket}. Retcode: {result.retcode}")
    else:
        print(f"Uppdaterade SL för ticket {ticket} till {sl_price}")

def adjust_pips_for_digits(symbol, pips):
    """
    Justerar pips baserat på antalet decimaler i symbolens pris.
    Om symbolen har 5 decimaler (t.ex. EURUSD), delas pips med 10.
    Om symbolen har 3 decimaler (t.ex. USDJPY), delas pips med 1.
    Om symbolen har 2 decimaler (t.ex. oljepriser), multipliceras pips med 10.

    :param symbol: Symbolens namn (t.ex. EURUSD, USDJPY).
    :param pips: Antalet pips att justera.
    :return: Justerat antal pips.
    """
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        print(f"Failed to retrieve symbol info for {symbol}. Returning unadjusted pips.")
        return pips

    digits = symbol_info.digits
    if digits == 5:  # Vanliga valutapar med 5 decimaler
        adjusted_pips = pips / 10
    elif digits == 3:  # Valutapar som USDJPY med 3 decimaler
        adjusted_pips = pips  # Ingen förändring
    elif digits == 2:  # Symboler med 2 decimaler, exempelvis oljepriser
        adjusted_pips = pips * 10
    else:
        print(f"Unhandled number of digits: {digits} for symbol {symbol}. Returning unadjusted pips.")
        adjusted_pips = pips  # Default, ingen förändring

    return adjusted_pips
