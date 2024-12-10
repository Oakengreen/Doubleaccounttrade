from settings import (
    initial_stop_level, initial_stop_percent, account_size,
    number_of_pips, top_up_levels1, top_up_levels2, top_up_levels3,
    target_gain_percent
)
import MetaTrader5 as mt5
import pandas as pd

if not mt5.initialize():
    print("MetaTrader 5 initialization failed. Ensure that the terminal is running and properly configured.")

# Konvertera pips till points
top_up_levels1_points = top_up_levels1 * 10  # 1 pip = 10 points
top_up_levels2_points = top_up_levels2 * 10
top_up_levels3_points = top_up_levels3 * 10

def calculate_loss_in_dollars(initial_stop_percent, account_size):
    """
    Beräknar förlusten i dollar för den första traden.
    :param initial_stop_percent: Procent av kontot som riskeras.
    :param account_size: Totalt kontosaldo.
    :return: Förlust i dollar.
    """
    loss_in_dollars = (initial_stop_percent / 100) * account_size
    return loss_in_dollars


def calculate_initial_lot_size(loss_in_dollars, initial_stop_level, pip_value):
    """
    Beräknar initial lot size för den första traden (marknadsorder).
    :param loss_in_dollars: Förlusten i dollar för traden.
    :param initial_stop_level: Antal pips till breakeven-nivån.
    :param pip_value: Pipvärdet i kontovaluta.
    :return: Initial lot size avrundad till två decimaler.
    """
    # Beräkna lot size
    lot_size = loss_in_dollars / (initial_stop_level * pip_value)

    # Skala ned till två decimaler
    lot_size = round(lot_size, 2)

    return lot_size


def get_pip_value(symbol):
    """
    Hämtar pip-värdet för en given symbol från MetaTrader 5.
    :param symbol: Symbolens namn (t.ex. 'GBPJPY').
    :return: Pip-värdet för symbolen.
    """

    # Hämta symbolinformation
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None or not symbol_info.visible:
        print(f"Symbol {symbol} information not found or symbol not visible.")
        return None

    # Använd trade_tick_value för att hämta pip-värdet
    pip_value = symbol_info.trade_tick_value

    # Kontrollera att pip_value är giltigt
    if pip_value <= 0:
        print(f"Invalid pip value for {symbol}.")
        return None

    print(f"Symbol Info: ask={symbol_info.ask}, bid={symbol_info.bid}, point={symbol_info.point}")

    return pip_value


def get_spread_in_pips(symbol):
    """
    Hämtar spread i pips för en given symbol baserat på skillnaden mellan ASK och BID.
    :param symbol: Symbolens namn (t.ex. 'GBPJPY').
    :return: Spread i pips.
    """
    # Hämta symbolinformation
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Symbol {symbol} information not found.")
        return None

    if not symbol_info.visible:
        print(f"Symbol {symbol} is not visible. Trying to select the symbol...")
        if not mt5.symbol_select(symbol, True):
            print(f"Failed to select {symbol}.")
            return None

    # Kontrollera värdena
    print(f"Symbol Info: ask={symbol_info.ask}, bid={symbol_info.bid}, point={symbol_info.point}")

    # Beräkna spread i pips
    spread_in_pips = (symbol_info.ask - symbol_info.bid) / symbol_info.point / 10

    if spread_in_pips <= 0:
        print(f"Invalid spread for {symbol}: {spread_in_pips}")
        return None

    return spread_in_pips


def calculate_pip_gain(number_of_pips, spread_in_pips, top_up_levels1, top_up_levels2, top_up_levels3):
    """
    Beräknar pip gain för initial order och stop orders.
    """
    pip_gains = {
        'initial': round(number_of_pips - spread_in_pips, 2),
        'stop_1': round(number_of_pips * (1 - (top_up_levels1 / 100)) - spread_in_pips, 2),
        'stop_2': round(number_of_pips * (1 - (top_up_levels2 / 100)) - spread_in_pips, 2),
        'stop_3': round(number_of_pips * (1 - (top_up_levels3 / 100)) - spread_in_pips, 2)
    }
    return pip_gains


def calculate_gain_in_dollars(lot_size, pip_gain, pip_value):
    """
    Beräknar gain in $ för en given order.
    :param lot_size: Lot storlek.
    :param pip_gain: Pip gain.
    :param pip_value: Pip värde.
    :return: Gain in $.
    """
    return lot_size * pip_gain * pip_value


def summarize_results(pip_value, spread_in_pips, loss_in_dollars, initial_lot_size, pip_gains, gain_in_dollars_initial):
    print("\n--- Trade Summary ---")
    print(f"Symbol: {symbol}")
    print(f"Pip Value: {pip_value:.2f}")
    print(f"Spread in Pips: {spread_in_pips:.2f}")
    print(f"Loss in $: {loss_in_dollars:.2f}")
    print(f"Initial Lot Size: {initial_lot_size} lots")
    print(f"Pip Gains: {pip_gains}")
    print(f"Gain in $ for Initial Order: {gain_in_dollars_initial:.2f}")


# Symbol
symbol = "XAUUSD"

# Hämta spread_in_pips
spread_in_pips = get_spread_in_pips(symbol)
if spread_in_pips is None:
    print("Failed to retrieve spread in pips.")
else:
    print(f"Spread in pips for {symbol}: {spread_in_pips:.2f}")

# Hämta pip_value
pip_value = get_pip_value(symbol)
if pip_value is None:
    print("Failed to retrieve pip value.")
else:
    print(f"Pip value for {symbol}: {pip_value:.2f}")

# Beräkna förlust i dollar
loss_in_dollars = calculate_loss_in_dollars(initial_stop_percent, account_size)


# Beräkna initial lot size
initial_lot_size = calculate_initial_lot_size(loss_in_dollars, initial_stop_level, pip_value)

# Beräkna pip gains
pip_gains = calculate_pip_gain(number_of_pips, spread_in_pips, top_up_levels1, top_up_levels2, top_up_levels3)

# Beräkna total_gain
total_gain = (account_size * target_gain_percent) / 100
print(f"Total Gain Target: {total_gain:.2f}")

# Beräkna gain in $ för initialorder
gain_in_dollars_initial = calculate_gain_in_dollars(initial_lot_size, pip_gains['initial'], pip_value)

# Beräkna Gain in $ för stop_1
gain_in_dollars_stop_1 = ((total_gain - gain_in_dollars_initial) * top_up_levels1) / (top_up_levels1 + top_up_levels2 + top_up_levels3)
print(f"Gain in $ for Stop 1: {gain_in_dollars_stop_1:.2f}")

# Beräkna Gain in $ för stop_2
gain_in_dollars_stop_2 = ((total_gain - gain_in_dollars_initial) * top_up_levels2) / (top_up_levels1 + top_up_levels2 + top_up_levels3)
print(f"Gain in $ for Stop 2: {gain_in_dollars_stop_2:.2f}")

# Beräkna Gain in $ för stop_3
gain_in_dollars_stop_3 = ((total_gain - gain_in_dollars_initial) * top_up_levels3) / (top_up_levels1 + top_up_levels2 + top_up_levels3)
print(f"Gain in $ for Stop 3: {gain_in_dollars_stop_3:.2f}")

summarize_results(pip_value, spread_in_pips, loss_in_dollars, initial_lot_size, pip_gains, gain_in_dollars_initial)


# Break even at 1st stop - START
# Grundläggande variabler
pips_initial = 0
pips_stop_1 = top_up_levels1 / number_of_pips
pips_stop_2 = number_of_pips / (top_up_levels2 / 10)
pips_stop_3 = number_of_pips / (top_up_levels3 / 10)

# Lots för stop_1
lots_stop_1 = gain_in_dollars_stop_1 / (pip_gains['stop_1'] * pip_value)

# Nivåer för initial och stop_1 (avrundade och multiplicerade med 10)
level_initial = (lots_stop_1 / initial_lot_size) * pips_stop_2 / (lots_stop_1 / initial_lot_size)
level_stop_1 = level_initial  # Samma som level_initial, också avrundat

# Spread för initial och stop_1
spread_initial = initial_lot_size * spread_in_pips * pip_value
spread_stop_1 = lots_stop_1 * spread_in_pips * pip_value

# Pip gains för initial och stop_1
pip_gains_initial = level_initial
pip_gain_stop_1 = (level_initial - pips_stop_1) * -1

# Resultat för initial och stop_1
result_initial = initial_lot_size * pip_gains_initial * pip_value
result_stop_1 = lots_stop_1 * pip_gain_stop_1 * (-pip_value)

# Totalt
total_spread = pip_value + spread_stop_1
total_pip_gains = pip_gains_initial - pip_gain_stop_1
total_result_dollar = result_initial + result_stop_1

# Skapa data för tabellen
data = {
    "Level": [round(level_initial, 0), round(level_stop_1, 0)],
    "Spread": [spread_initial, spread_stop_1],
    "Lots": [round(initial_lot_size, 2), round(lots_stop_1, 2)],
    "Pip Gain": [round(pip_gains_initial, 1), round(pip_gain_stop_1, 1)],
    "Result": [round(result_initial, 1), round(result_stop_1, 1)]
}

# Skapa DataFrame
df = pd.DataFrame(data, index=["Initial", "Stop_1"])

# Lägg till totalsumma längst ned
df.loc["Total"] = [
    "",
    round(total_spread, 1),
    "",
    round(total_pip_gains, 1),
    round(total_result_dollar, 1)
]

# Visa tabellen
print(df)

print(f"lots_stop_1: {lots_stop_1}")
print(f"initial_lot_size: {initial_lot_size}")
print(f"level_initial: {level_initial}")

# Debugutskrifter för pips_stop_1, pips_stop_2, och pips_stop_3
print(f"pips_stop_1: {pips_stop_1}")
print(f"pips_stop_2: {pips_stop_2}")
print(f"pips_stop_3: {pips_stop_3}")

# Break even at 1st stop - END
