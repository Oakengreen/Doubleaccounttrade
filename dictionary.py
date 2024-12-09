"Input into the EA settings": {
    "coordinates": "C5:D18",
    "data": [
        {"name": "Account size", "value": "$1,250", "formula": None, "coordinates": "D7"},
        {"name": "% gain targeted", "value": "10%", "formula": None, "coordinates": "D8"},
        {"name": "Number of pips", "value": "100", "formula": None, "coordinates": "D9"},
        {"name": "Initial stop", "value": "50", "formula": None, "coordinates": "D10"},
        {"name": "% of account to be risked", "value": "4%", "formula": None, "coordinates": "D11"},
        {"name": "Initial breakeven stop level", "value": "40", "formula": None, "coordinates": "D12"},
        {"name": "Top up level 1", "value": "35%", "formula": None, "coordinates": "D13"},
        {"name": "Top up level 2", "value": "50%", "formula": None, "coordinates": "D14"},
        {"name": "Top up level 3", "value": "65%", "formula": None, "coordinates": "D15"},
        {"name": "Min stop distance", "value": "6,00", "formula": None, "coordinates": "D16"},
        {"name": "Value of a pip", "value": "10", "formula": None, "coordinates": "D17"},
        {"name": "Spread in Pips", "value": "13,00", "formula": None, "coordinates": "D18"}
    ]
}


"Trading Plan Overview": {
    "position": "J6:O12",
    "columns": ["Trade", "Levels", "Pips", "Lots", "Pip gain", "Gain in $"],
    "formulas_with_results": {
        "Initial": {
            "Levels": {"formula": "0", "result": 0, "coordinates": "K7"},
            "Pips": {"formula": "0", "result": 0, "coordinates": "L7"},
            "Lots": {"formula": "=+M25", "result": 0.10, "coordinates": "M7"},
            "Pip gain": {"formula": "=+D9-D18", "result": 87.00, "coordinates": "N7"},
            "Gain in $": {"formula": "=ROUNDUP(+M8*N8*D17;0)", "result": 87, "coordinates": "O7"}
        },
        "Topup1": {
            "Levels": {"formula": "=+D13", "result": 35, "coordinates": "K8"},
            "Pips": {"formula": "=ROUNDUP(+K9*D9;0)", "result": 35, "coordinates": "L8"},
            "Lots": {"formula": "=ROUNDUP(+O9/N9/D17;2)", "result": 0.02, "coordinates": "M8"},
            "Pip gain": {"formula": "=(+D$9*(1-K9))-D$18", "result": 52.00, "coordinates": "N8"},
            "Gain in $": {"formula": "=ROUNDUP((O12-O8)*D13/(D13+D14+D15);0)", "result": 9, "coordinates": "O8"}
        },
        "Topup2": {
            "Levels": {"formula": "=+D14", "result": 50, "coordinates": "K9"},
            "Pips": {"formula": "=ROUNDUP(+D9*K10;0)", "result": 50, "coordinates": "L9"},
            "Lots": {"formula": "=ROUNDUP(OM(D14=0;0;+O10/N10/D17);2)", "result": 0.04, "coordinates": "M9"},
            "Pip gain": {"formula": "=(+D$9*(1-K10))-D$18", "result": 37.00, "coordinates": "N9"},
            "Gain in $": {"formula": "=ROUNDUP((O12-O8)*D14/(D13+D14+D15);0)", "result": 13, "coordinates": "O9"}
        },
        "Topup3": {
            "Levels": {"formula": "=+D15", "result": 65, "coordinates": "K10"},
            "Pips": {"formula": "=ROUNDUP(+D9*K11;0)", "result": 65, "coordinates": "L10"},
            "Lots": {"formula": "=ROUNDUP(OM(D15=0;0;+O11/N11/D17);2)", "result": 0.08, "coordinates": "M10"},
            "Pip gain": {"formula": "=ROUND(OM(D15=0;0;+D9-L11-D18);0)", "result": 22.00, "coordinates": "N10"},
            "Gain in $": {"formula": "=OM(D15=0;0;(ROUND((O12-O8)*D15/(D13+D14+D15);0)))", "result": 16, "coordinates": "O10"}
        },
        "Total": {
            "Gain in $": {"formula": "=ROUND(+D7*D8;0)", "result": 125, "coordinates": "O12"}
        }
    }
}


"Margin of Safety": {
    "position": "J15:N20",
    "columns": ["Trade", "Stop Type", "Pips", "<--Goal"],
    "formulas_with_results": {
        "Initial": {
            "Stop Type": {"formula": "Stoploss", "result": "Stoploss"},
            "Pips": {"formula": "=+D10", "result": 50},
            "<--Goal": {"formula": "balance", "result": "balance"}
        },
        "Topup1": {
            "Stop Type": {"formula": "Breakeven", "result": "Breakeven"},
            "Pips": {"formula": "=+U9", "result": 29},
            "<--Goal": {"formula": "balance", "result": "balance"}
        },
        "Topup2": {
            "Stop Type": {"formula": "Breakeven", "result": "Breakeven"},
            "Pips": {"formula": "=+U16", "result": 33},
            "<--Goal": {"formula": "balance", "result": "balance"}
        },
        "Topup3": {
            "Stop Type": {"formula": "Breakeven", "result": "Breakeven"},
            "Pips": {"formula": "=OM(D15=0;\"N/A\";-U24)", "result": 32},
            "<--Goal": {"formula": "balance", "result": "balance"}
        }
    }
}

"Initial Stop": {
    "position": "J23:O25",
    "columns": ["", "Lots", "Stop", "Loss in $"],
    "formulas_with_results": {
        "": {
            "Lots": {"formula": "=ROUND((+O25/N25/D17);2)", "result": 0.1},
            "Stop": {"formula": "=+D10", "result": 50.00},
            "Loss in $": {"formula": "=+D7*D11", "result": "$50"}
        }
    }
}

"Break even stop at 1st top-up": {
    "position": "Q6:V10",
    "columns": ["Level", "Spread", "Lots", "Pip Gains", "Result"],
    "formulas_with_results": {
        "Initial": {
            "Level": {"formula": "=ROUNDUP((+T9/T8)*L9/(1+(M9/M8));0)", "result": None},
            "Spread": {"formula": "=+T8*D$18*D$17", "result": None},
            "Lots": {"formula": "=+M8", "result": None},
            "Pip Gains": {"formula": "=+R8", "result": None},
            "Result": {"formula": "=+T8*U8*D17", "result": None},
        },
        "Topup1": {
            "Level": {"formula": "=+R8", "result": None},
            "Spread": {"formula": "=+T9*D$18*D$17", "result": None},
            "Lots": {"formula": "=+M9", "result": None},
            "Pip Gains": {"formula": "=(+R8-L9)*-1", "result": None},
            "Result": {"formula": "=+T9*U9*-D17", "result": None},
        },
        "Totals": {
            "Spread": {"formula": "=+S8+S9", "result": None},
            "Pip Gains": {"formula": "=+U8-U9", "result": None},
            "Result": {"formula": "=SUM(V8:V9)", "result": None},
        },
    },
}

"Break even stop at 2nd top-up": {
    "position": "Q12:V17",
    "columns": ["Level", "Spread", "Lots", "Pip Gains", "Result"],
    "formulas_with_results": {
        "Initial": {
            "Level": {"formula": "=ROUNDUP((((+M9*L9)+(M10*L10))/(M8+M9+M10));0)", "result": None},
            "Spread": {"formula": "=OM(D$14=0;\"    N/A\";+T14*D$18*D$17)", "result": None},
            "Lots": {"formula": "=OM(D$14=0;\"     N/A\";+M8)", "result": None},
            "Pip Gains": {"formula": "=OM(D14=0;\"     N/A\";+R14)", "result": None},
            "Result": {"formula": "=OM(D14=0;\"   N/A\";+T14*U14*D17)", "result": None},
        },
        "Topup1": {
            "Level": {"formula": "=+R14", "result": None},
            "Spread": {"formula": "=OM(D$14=0;\"    N/A\";+T15*D$18*D$17)", "result": None},
            "Lots": {"formula": "=OM(D$14=0;\"     N/A\";+M9)", "result": None},
            "Pip Gains": {"formula": "=OM(D14=0;\"     N/A\";+R15-L9)", "result": None},
            "Result": {"formula": "=OM(D14=0;\"   N/A\";+T15*U15*D17)", "result": None},
        },
        "Topup2": {
            "Level": {"formula": "=+R15", "result": None},
            "Spread": {"formula": "=OM(D$14=0;\"    N/A\";+T16*D$18*D$17)", "result": None},
            "Lots": {"formula": "=OM(D$14=0;\"     N/A\";+M10)", "result": None},
            "Pip Gains": {"formula": "=OM(D14=0;\"     N/A\";(+R16-L10)*-1)", "result": None},
            "Result": {"formula": "=OM(D14=0;\"   N/A\";+U16*T16*-D17)", "result": None},
        },
        "Totals": {
            "Spread": {"formula": "=SUM(S14:S16)", "result": None},
            "Result": {"formula": "=SUM(V14:V16)", "result": None},
        },
    },
}

"Break even stop at 3rd top-up": {
    "position": "Q19:V25",
    "columns": ["Level", "Spread", "Lots", "Pip Gains", "Result"],
    "formulas_with_results": {
        "Initial": {
            "Level": {"formula": "=OM(D15=0;\"NA\";ROUNDUP((((+M9*L9)+(M10*L10)+(M11*L11))/(M8+M9+M10+M11));0))", "result": None},
            "Spread": {"formula": "=OM(D15=0;\"N/A\";+S8)", "result": None},
            "Lots": {"formula": "=OM(D15=0;\"N/A\";+M8)", "result": None},
            "Pip Gains": {"formula": "=+R21", "result": None},
            "Result": {"formula": "=OM(D15=0;\"NA\";+T21*U21*D17)", "result": None},
        },
        "Topup1": {
            "Level": {"formula": "=+R21", "result": None},
            "Spread": {"formula": "=+S15", "result": None},
            "Lots": {"formula": "=+M9", "result": None},
            "Pip Gains": {"formula": "=OM(D15=0;\"NA\";+R22-L9)", "result": None},
            "Result": {"formula": "=OM(D15=0;\"NA\";+T22*U22*D17)", "result": None},
        },
        "Topup2": {
            "Level": {"formula": "=+R22", "result": None},
            "Spread": {"formula": "=+S16", "result": None},
            "Lots": {"formula": "=+M10", "result": None},
            "Pip Gains": {"formula": "=OM(D15=0;\"NA\";+R23-L10)", "result": None},
            "Result": {"formula": "=OM(D15=0;\"NA\";+T23*U23*D17)", "result": None},
        },
        "Topup3": {
            "Level": {"formula": "=+R23", "result": None},
            "Spread": {"formula": "=OM(D15=0;\"N/A\";+T24*D18*D17)", "result": None},
            "Lots": {"formula": "=+M11", "result": None},
            "Pip Gains": {"formula": "=OM(D15=0;\"NA\";(+U19-R24)*-1)", "result": None},
            "Result": {"formula": "=OM(D15=0;\"NA\";+T24*U24*D17)", "result": None},
        },
        "Totals": {
            "Spread": {"formula": "=SUM(S21:S24)", "result": None},
            "Result": {"formula": "=SUM(V21:V24)", "result": None},
        },
    },
}

"Q6-->V10": {
    "description": "=== Break even stop at 1st top-up at",
    "formulas": {
        "level": {"Initial": "=ROUNDUP((+T9/T8)*L9/(1+(M9/M8));0)", "Topup1": "=+R8", "sum": "=+S8+S9"},
        "spread": {"Initial": "=+T8*D$18*D$17", "Topup1": "=+T9*D$18*D$17"},
        "lots": {"Initial": "=+M8", "Topup1": "=+M9"},
        "pip gains": {"Initial": "=+R8", "Topup1": "=(+R8-L9)*-1", "sum": "=+U8-U9"},
        "result": {"Initial": "=+T8*U8*D17", "Topup1": "=+T9*U9*-D17", "sum": "=SUM(V8:V9)"}
    },
    "coordinates": {
        "level": {"Initial": "Q6", "Topup1": "Q7", "sum": "Q8"},
        "spread": {"Initial": "R6", "Topup1": "R7"},
        "lots": {"Initial": "S6", "Topup1": "S7"},
        "pip gains": {"Initial": "T6", "Topup1": "T7", "sum": "T8"},
        "result": {"Initial": "U6", "Topup1": "U7", "sum": "U8"}
    },
    "reference_values": {
        "level": {"Initial": 6, "Topup1": 6, "sum": 15.6},
        "spread": {"Initial": 13.0, "Topup1": 2.6},
        "lots": {"Initial": 0.10, "Topup1": 0.02},
        "pip gains": {"Initial": 6, "Topup1": 29, "sum": -23},
        "result": {"Initial": "$ 6", "Topup1": "-$ 6", "sum": "$ 0"}
    }
}

"Q12-->V17": {
    "description": "=== Break even stop at 2nd top-up at",
    "formulas": {
        "level": {
            "Initial": "=ROUNDUP((((+M9*L9)+(M10*L10))/(M8+M9+M10));0)",
            "Topup1": "=+R14",
            "Topup2": "=+R15",
            "sum": "=SUM(S14:S16)"
        },
        "spread": {
            "Initial": "=OM(D$14=0;'N/A';+T14*D$18*D$17)",
            "Topup1": "=OM(D$14=0;'N/A';+T15*D$18*D$17)",
            "Topup2": "=OM(D$14=0;'N/A';+T16*D$18*D$17)"
        },
        "lots": {
            "Initial": "=OM(D$14=0;'N/A';+M8)",
            "Topup1": "=OM(D$14=0;'N/A';+M9)",
            "Topup2": "=OM(D$14=0;'N/A';+M10)"
        },
        "pip gains": {
            "Initial": "=OM(D$14=0;'N/A';+R14)",
            "Topup1": "=OM(D$14=0;'N/A';+R15-L9)",
            "Topup2": "=OM(D$14=0;'N/A';(+R16-L10)*-1)",
            "sum": "=+U8-U9"
        },
        "result": {
            "Initial": "=OM(D$14=0;'N/A';+T14*U14*D17)",
            "Topup1": "=OM(D$14=0;'N/A';+T15*U15*D17)",
            "Topup2": "=OM(D$14=0;'N/A';+U16*T16*-D17)",
            "sum": "=SUM(V14:V16)"
        }
    },
    "coordinates": {
        "level": {"Initial": "Q12", "Topup1": "Q13", "Topup2": "Q14", "sum": "Q15"},
        "spread": {"Initial": "R12", "Topup1": "R13", "Topup2": "R14"},
        "lots": {"Initial": "S12", "Topup1": "S13", "Topup2": "S14"},
        "pip gains": {"Initial": "T12", "Topup1": "T13", "Topup2": "T14", "sum": "T15"},
        "result": {"Initial": "U12", "Topup1": "U13", "Topup2": "U14", "sum": "U15"}
    },
    "reference_values": {
        "level": {"Initial": 17, "Topup1": 17, "Topup2": 17, "sum": 20.8},
        "spread": {"Initial": 13.0, "Topup1": 2.6, "Topup2": 5.2},
        "lots": {"Initial": 0.10, "Topup1": 0.02, "Topup2": 0.04},
        "pip gains": {"Initial": 17, "Topup1": -18, "Topup2": 33, "sum": 0},
        "result": {"Initial": "$ 17", "Topup1": "-$ 4", "Topup2": "-$ 13", "sum": "$ 0"}
    }
}

"Q19-->V25": {
    "description": "=== Break even stop at 3rd top-up at",
    "formulas": {
        "level": {
            "Initial": "=OM(D15=0;'NA';ROUNDUP((((+M9*L9)+(M10*L10)+(M11*L11))/(M8+M9+M10+M11));0))",
            "Topup1": "=+R21",
            "Topup2": "=+R22",
            "Topup3": "=+R23",
            "sum": "=SUM(S21:S24)"
        },
        "spread": {
            "Initial": "=OM(D15=0;'N/A';+S8)",
            "Topup1": "=+S15",
            "Topup2": "=+S16",
            "Topup3": "=OM(D15=0;'N/A';+T24*D18*D17)"
        },
        "lots": {
            "Initial": "=OM(D15=0;'N/A';+M8)",
            "Topup1": "=+M9",
            "Topup2": "=+M10",
            "Topup3": "=+M11"
        },
        "pip gains": {
            "Initial": "=+R21",
            "Topup1": "=OM(D15=0;'NA';+R22-L9)",
            "Topup2": "=OM(D15=0;'NA';+R23-L10)",
            "Topup3": "=OM(D15=0;'NA';(+U19-R24)*-1)"
        },
        "result": {
            "Initial": "=OM(D15=0;'NA';+T21*U21*D17)",
            "Topup1": "=OM(D15=0;'NA';+T22*U22*D17)",
            "Topup2": "=OM(D15=0;'NA';+T23*U23*D17)",
            "Topup3": "=OM(D15=0;'NA';+T24*U24*D17)",
            "sum": "=SUM(V21:V24)"
        }
    },
    "coordinates": {
        "level": {"Initial": "Q19", "Topup1": "Q20", "Topup2": "Q21", "Topup3": "Q22", "sum": "Q23"},
        "spread": {"Initial": "R19", "Topup1": "R20", "Topup2": "R21", "Topup3": "R22"},
        "lots": {"Initial": "S19", "Topup1": "S20", "Topup2": "S21", "Topup3": "S22"},
        "pip gains": {"Initial": "T19", "Topup1": "T20", "Topup2": "T21", "Topup3": "T22"},
        "result": {"Initial": "U19", "Topup1": "U20", "Topup2": "U21", "Topup3": "U22", "sum": "U23"}
    },
    "reference_values": {
        "level": {"Initial": 33, "Topup1": 33, "Topup2": 33, "Topup3": 33, "sum": 31.2},
        "spread": {"Initial": 13.0, "Topup1": 2.6, "Topup2": 5.2, "Topup3": 10.4},
        "lots": {"Initial": 0.10, "Topup1": 0.02, "Topup2": 0.04, "Topup3": 0.08},
        "pip gains": {"Initial": 33, "Topup1": -2, "Topup2": -17, "Topup3": -32},
        "result": {"Initial": "$ 33", "Topup1": "-$ 0", "Topup2": "-$ 7", "Topup3": "-$ 26", "sum": "$ 0"}
    }
}
