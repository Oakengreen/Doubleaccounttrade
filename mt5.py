import MetaTrader5 as mt5

if not mt5.initialize():
    print("MetaTrader 5 initialization failed. Ensure that the terminal is running and properly configured.")

symbol = "GBPJPY"

symbol_info = mt5.symbol_info(symbol)

print(symbol_info.digits)