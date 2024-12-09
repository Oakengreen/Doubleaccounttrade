import json
# Ladda in JSON-data
with open("excel_data.json", "r") as f:
    json_data = json.load(f)

# Nu har vi JSON-data i en Python-dictionary
#print(json_data)

# Exempel på hur man får tag på värdet i cell D7:
print(json_data["Breakeven Stops"]["D7"]["value"])