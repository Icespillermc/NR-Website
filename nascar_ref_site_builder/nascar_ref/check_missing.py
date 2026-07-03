import json
from parser_xlsx import parse_workbook

with open('driver_birth_years.json') as f:
    bdays = json.load(f)

data = parse_workbook(r'C:\Users\eelbo\Desktop\Ethan\NR Website\NASCAR SIM.xlsx')
missing = []
for name in data['career']:
    if name not in bdays:
        missing.append(name)

print(f'Total career drivers: {len(data["career"])}')
print(f'Drivers with birth years: {len(bdays)}')
print(f'Missing birth years: {len(missing)}')
print()
for m in missing:
    print(m)
