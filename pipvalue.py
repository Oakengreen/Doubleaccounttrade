
def get_pip_value(symbol):
    """
    Hämtar pip-värdet för en given symbol från MetaTrader 5.
    :param symbol: Symbolens namn (t.ex. 'GBPJPY').
    :return: Pip-värdet för symbolen.
    """
    # Anslut till MetaTrader 5
    if not mt5.initialize():
        print("MetaTrader 5 initialization failed")
        return None

    # Hämta symbolinformation
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Symbol {symbol} not found")
        return None

    # Kontrollera om symbolen är aktiv
    if not symbol_info.visible:
        print(f"Symbol {symbol} is not visible, attempting to make it visible")
        if not mt5.symbol_select(symbol, True):
            print(f"Failed to select symbol {symbol}")
            return None

    # Inspektera symbolinformationen
    print(f"Symbol info for {symbol}: {symbol_info}")

    # Beräkna pip-värde
    pip_size = 0.01 if symbol_info.digits == 3 else 0.0001
    pip_value = pip_size * symbol_info.trade_contract_size / symbol_info.point

    return pip_value