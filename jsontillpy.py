def convert_excel_formula_to_python(expr):
    if expr is None:
        return None

    # Ta bort ledande '='
    expr = expr.lstrip('=')
    # Ta bort ledande '+' om det finns
    expr = re.sub(r'^\+', '', expr)

    # Hantera IF-funktioner:
    # Excel: IF(condition, value_if_true, value_if_false)
    # Python: (value_if_true if condition else value_if_false)
    # Ex. =IF(D15=0,"NA",T22*U22*D17)
    # condition: D15=0 -> values['D15']==0
    # true: "NA"
    # false: values['T22']*values['U22']*values['D17']

    # Detta är en enkel hantering av IF:
    def if_replacer(match):
        # match: IF(...,...,...)
        inner = match.group(1)  # Allt inom IF(...)
        # Dela upp på kommatecken utanför parenteser (enkel lösning, förutsätter inga inbäddade IF)
        parts = [p.strip() for p in inner.split(',')]
        if len(parts) != 3:
            return match.group(0)  # Okänt format, returnera original

        condition, val_if_true, val_if_false = parts

        # Konvertera condition (t.ex. D15=0) till Python:
        # Ersätt '=' med '==' om det är en enkel jämförelse
        # Detta är förenklat och förutsätter enkel form: D15=0
        condition = condition.replace('=', '==')

        # Konvertera cellreferenser till values['cell']
        condition = re.sub(r'([A-Z]{1,3}\d+)', r"values['\1']", condition)
        val_if_true = re.sub(r'([A-Z]{1,3}\d+)', r"values['\1']", val_if_true)
        val_if_false = re.sub(r'([A-Z]{1,3}\d+)', r"values['\1']", val_if_false)

        return f"({val_if_true} if {condition} else {val_if_false})"

    expr = re.sub(r'IF\((.*?)\)', if_replacer, expr)

    # Ersätt cellreferenser med values['C5'] etc.
    # Detta görs endast om de ej redan konverterats. Vi tar alla cellreferenser:
    expr = re.sub(r'([A-Z]{1,3}\d+)', r"values['\1']", expr)

    # Ta bort eventuella '+' som prefix på termer:
    expr = re.sub(r'\+\s*values', 'values', expr)

    # Kvarstående Excel-funktioner som ROUNDUP, etc. kan behöva ersättas med Python-funktioner
    # Exempel: ROUNDUP(x,0) -> math.ceil(x) om det är 0 decimaler.
    # Här gör vi en enkel ersättning för ROUNDUP(x,0) med int(math.ceil(x))

    # För enkelhets skull: ersätt ROUNDUP(expr,0) med int(math.ceil(expr))
    # Detta förutsätter att du importerat math: from math import ceil
    def roundup_replacer(match):
        inner = match.group(1)
        parts = [p.strip() for p in inner.split(',')]
        if len(parts) == 2 and parts[1] == '0':
            return f"int(math.ceil({parts[0]}))"
        else:
            # Om det inte är just 0 decimaler, får du anpassa mer avancerat
            # Här returneras originalet om vi inte kan hantera det enkelt:
            return match.group(0)

    expr = re.sub(r'ROUNDUP\((.*?)\)', roundup_replacer, expr)

    # Ersätt Excel-dollarreferenser D$18 osv, med bara D18 (tar bort $)
    expr = expr.replace('$', '')

    return expr


# Skapa en dictionary för formler
formulas_dict = {}

for cell, content in data.get("Breakeven Stops", {}).items():
    formula = content.get("formula")
    if formula:
        python_expr = convert_excel_formula_to_python(formula)
        formulas_dict[cell] = python_expr

print(formulas_dict)
