import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Create sample SuperStore data since your Excel file is corrupted
print("🔄 Creating sample SuperStore data...")

# Generate sample data
np.random.seed(42)
n_orders = 1000

# Sample data lists
regions = ['East', 'West', 'Central', 'South']
states = ['California', 'Texas', 'New York', 'Florida', 'Illinois', 'Pennsylvania', 'Ohio', 'Georgia', 'North Carolina', 'Michigan']
cities = ['Los Angeles', 'New York', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
categories = ['Office Supplies', 'Furniture', 'Technology']
subcategories = {
    'Office Supplies': ['Paper', 'Binders', 'Fasteners', 'Art', 'Storage', 'Supplies'],
    'Furniture': ['Chairs', 'Tables', 'Bookcases', 'Furnishings'],
    'Technology': ['Phones', 'Accessories', 'Copiers', 'Machines']
}
segments = ['Consumer', 'Corporate', 'Home Office']
ship_modes = ['Standard Class', 'Second Class', 'First Class', 'Same Day']

# Generate Orders data
orders_data = []
for i in range(n_orders):
    order_date = datetime(2021, 1, 1) + timedelta(days=random.randint(0, 1095))
    ship_date = order_date + timedelta(days=random.randint(1, 7))
    category = random.choice(categories)
    subcategory = random.choice(subcategories[category])
    
    orders_data.append({
        'Order ID': f'US-{2021 + i // 365}-{i:06d}',
        'Order Date': order_date,
        'Ship Date': ship_date,
        'Ship Mode': random.choice(ship_modes),
        'Customer ID': f'CU-{random.randint(10000, 99999)}',
        'Sales Rep': 'Organic',
        'Location ID': f'{random.randint(10000, 99999)},{random.choice(cities)}',
        'Product ID': f'{category[:3].upper()}-{subcategory[:2].upper()}-{random.randint(1000000, 9999999)}',
        'Quantity': random.randint(1, 10),
        'Discount': round(random.uniform(0, 0.5), 2),
        'Sales': round(random.uniform(10, 2000), 2),
        'Profit': round(random.uniform(-100, 500), 2)
    })

orders_df = pd.DataFrame(orders_data)

# Generate Location data
location_data = []
used_locations = set()
for _, row in orders_df.iterrows():
    if row['Location ID'] not in used_locations:
        location_id = row['Location ID']
        city = location_id.split(',')[1]
        location_data.append({
            'Location ID': location_id,
            'City': city,
            'State': random.choice(states),
            'Postal Code': random.randint(10000, 99999),
            'Region': random.choice(regions)
        })
        used_locations.add(location_id)

location_df = pd.DataFrame(location_data)

# Generate Customer data
customer_data = []
used_customers = set()
first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Chris', 'Amy', 'Robert', 'Emily']
last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']

for _, row in orders_df.iterrows():
    if row['Customer ID'] not in used_customers:
        customer_data.append({
            'Customer ID': row['Customer ID'],
            'Customer Name': f"{random.choice(first_names)} {random.choice(last_names)}",
            'Segment': random.choice(segments)
        })
        used_customers.add(row['Customer ID'])

customers_df = pd.DataFrame(customer_data)

# Generate Product data
product_data = []
used_products = set()
for _, row in orders_df.iterrows():
    if row['Product ID'] not in used_products:
        category = random.choice(categories)
        subcategory = random.choice(subcategories[category])
        product_data.append({
            'Product ID': row['Product ID'],
            'Category': category,
            'Sub-Category': subcategory,
            'Product Name': f"Sample {subcategory} Product"
        })
        used_products.add(row['Product ID'])

products_df = pd.DataFrame(product_data)

# Generate Sales Team data
salesteam_df = pd.DataFrame([
    {'Sales Rep': 'Organic', 'Sales Team': 'Organic', 'Sales Team Manager': 'Organic'},
    {'Sales Rep': 'John Smith', 'Sales Team': 'Alpha', 'Sales Team Manager': 'Manager A'},
    {'Sales Rep': 'Jane Doe', 'Sales Team': 'Beta', 'Sales Team Manager': 'Manager B'},
])

# Save all as CSV files
print("💾 Saving CSV files...")
orders_df.to_csv('orders.csv', index=False)
location_df.to_csv('location.csv', index=False)
customers_df.to_csv('customers.csv', index=False)
products_df.to_csv('products.csv', index=False)
salesteam_df.to_csv('salesteam.csv', index=False)

print("✅ Created CSV files:")
print(f"   - orders.csv ({len(orders_df)} rows)")
print(f"   - location.csv ({len(location_df)} rows)")
print(f"   - customers.csv ({len(customers_df)} rows)")
print(f"   - products.csv ({len(products_df)} rows)")
print(f"   - salesteam.csv ({len(salesteam_df)} rows)")

print("\n🚀 Next steps:")
print("1. Run your Streamlit app locally: streamlit run app.py")
print("2. Upload CSV files to GitHub: git add *.csv && git commit -m 'Add CSV files' && git push")
print("3. Your deployed app will now work!")
