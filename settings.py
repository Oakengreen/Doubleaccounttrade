import MetaTrader5 as mt5

# Initialize MetaTrader5 (om det behövs i settings)
if not mt5.initialize():
    print("MetaTrader 5 initialization failed. Ensure the terminal is running.")
    raise RuntimeError("Failed to initialize MetaTrader 5")

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
        adjusted_pips = pips * 100
    else:
        print(f"Unhandled number of digits: {digits} for symbol {symbol}. Returning unadjusted pips.")
        adjusted_pips = pips  # Default, ingen förändring

    return adjusted_pips

# Define the trading symbol once here
symbol = "EURUSD"

# Trading settings
account_size = 1000
target_gain_percent = 50
number_of_pips = adjust_pips_for_digits(symbol, 100)
initial_stop_percent = 4
initial_stop_level = adjust_pips_for_digits(symbol, 30)
top_up_levels1 = 35
top_up_levels2 = 50
top_up_levels3 = 65
min_stop_distance = 30
pip_value = 1
spread = 3
FILE_PATH = r"C:\\Program Files\\MetaTrader 5 IC Markets (SC)_OPTIMIZER\\terminal64.exe"
