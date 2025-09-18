import pandas as pd

# Convert Excel to CSV files
excel_file = 'SuperStore Data.xlsx'
sheet_names = ['Orders', 'Location', 'Calendar', 'Customers', 'Products', 'SalesTeam']

for sheet in sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet, engine='openpyxl')
    df.to_csv(f'{sheet.lower()}.csv', index=False)
    print(f"Created: {sheet.lower()}.csv")
