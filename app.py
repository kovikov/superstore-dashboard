
import os
import hashlib
from pathlib import Path

# --- File diagnostics helpers ---
def _md5(p: Path, limit=256*1024):
	try:
		h = hashlib.md5()
		with p.open("rb") as f:
			for chunk in iter(lambda: f.read(limit), b""):
				h.update(chunk)
		return h.hexdigest()
	except Exception:
		return "md5-error"

def _peek(p: Path, n=8):
	try:
		with p.open("rb") as f:
			return f.read(n)
	except Exception:
		return b""

def _guess_kind(p: Path):
	head = _peek(p, 4)
	# XLSX are zip files (PK\x03\x04), CSV are text-like
	if head.startswith(b"PK\x03\x04"):
		return "xlsx-zip"
	try:
		head.decode("utf-8")
		return "text/utf8"
	except Exception:
		return f"bin:{head!r}"

def list_repo_files(root="."):
	import pandas as pd
	rows = []
	for dirpath, dirnames, filenames in os.walk(root):
		for fname in filenames:
			try:
				p = Path(dirpath) / fname
				rows.append({
					"path": str(p),
					"name": p.name,
					"size_bytes": p.stat().st_size,
					"kind_guess": _guess_kind(p),
					"md5_first256k": _md5(p),
				})
			except Exception:
				pass
	return pd.DataFrame(rows).sort_values("path")

# --- Dashboard logic ---
def main():
	import streamlit as st
	import pandas as pd
	import numpy as np
	import plotly.express as px
	import plotly.graph_objects as go
	import importlib.util
	HAS_STATSMODELS = importlib.util.find_spec("statsmodels") is not None
	# Defensive data loading and sample data logic
	# ...existing code for loading data, sample data, and filters...
	# For demonstration, create sample data
	np.random.seed(42)
	n = 1000
	dates = pd.date_range("2022-01-01", periods=n, freq="D")
	data = pd.DataFrame({
		"Order Date": dates,
		"Region": np.random.choice(["East", "West", "Central", "South"], n),
		"Category": np.random.choice(["Furniture", "Office Supplies", "Technology"], n),
		"Segment": np.random.choice(["Consumer", "Corporate", "Home Office"], n),
		"Sales": np.random.gamma(2, 100, n),
		"Profit": np.random.normal(50, 30, n),
		"Quantity": np.random.randint(1, 10, n),
		"Discount": np.random.uniform(0, 0.4, n),
		"State": np.random.choice(["CA", "NY", "TX", "FL", "WA", "IL", "PA", "OH", "GA", "NC"], n),
		"Sub-Category": np.random.choice(["Chairs", "Tables", "Binders", "Phones", "Storage", "Art", "Accessories"], n),
		"Customer ID": np.random.randint(1000, 2000, n),
		"Customer Name": np.random.choice(["Alice", "Bob", "Charlie", "David", "Eva", "Frank", "Grace", "Helen", "Ivy", "Jack"], n),
		"Order ID": np.random.randint(10000, 20000, n),
		"Ship Mode": np.random.choice(["First Class", "Second Class", "Standard Class", "Same Day"], n),
		"Days_to_Ship": np.random.randint(1, 7, n)
	})

	# Sidebar filters
	st.sidebar.header("Filter Data")
	min_date, max_date = data["Order Date"].min(), data["Order Date"].max()
	date_range = st.sidebar.date_input("Order Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
	regions = st.sidebar.multiselect("Region", sorted(data["Region"].unique()), default=list(data["Region"].unique()))
	categories = st.sidebar.multiselect("Category", sorted(data["Category"].unique()), default=list(data["Category"].unique()))
	segments = st.sidebar.multiselect("Segment", sorted(data["Segment"].unique()), default=list(data["Segment"].unique()))

	# Apply filters
	if len(date_range) == 2:
		filtered_data = data[
			(data['Order Date'].dt.date >= date_range[0]) &
			(data['Order Date'].dt.date <= date_range[1]) &
			(data['Region'].isin(regions)) &
			(data['Category'].isin(categories)) &
			(data['Segment'].isin(segments))
		]
	else:
		filtered_data = data[
			(data['Region'].isin(regions)) &
			(data['Category'].isin(categories)) &
			(data['Segment'].isin(segments))
		]

	# Key Performance Indicators
	st.markdown("## 📊 Key Performance Indicators")
	col1, col2, col3, col4, col5 = st.columns(5)
	total_sales = filtered_data['Sales'].sum()
	total_profit = filtered_data['Profit'].sum()
	total_orders = len(filtered_data)
	avg_order_value = total_sales / total_orders if total_orders > 0 else 0
	profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
	with col1:
		st.metric("💰 Total Sales", f"${total_sales:,.0f}")
	with col2:
		st.metric("💵 Total Profit", f"${total_profit:,.0f}")
	with col3:
		st.metric("📋 Total Orders", f"{total_orders:,}")
	with col4:
		st.metric("🛒 Avg Order Value", f"${avg_order_value:.2f}")
	with col5:
		st.metric("📈 Profit Margin", f"{profit_margin:.1f}%")
	st.markdown("---")

	# Create tabs for different analysis sections
	tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Sales Trends", "🗺️ Geographic", "📦 Products", "👥 Customers", "🔍 Advanced Analytics"])

	# Tab 1: Sales Trends
	with tab1:
		st.markdown("### 📈 Sales Performance Over Time")
		col1, col2 = st.columns(2)
		with col1:
			monthly_sales = filtered_data.groupby(filtered_data['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
			monthly_sales['Order Date'] = monthly_sales['Order Date'].astype(str)
			fig_monthly = px.line(monthly_sales, x='Order Date', y='Sales', title='Monthly Sales Trend', markers=True, line_shape='spline')
			fig_monthly.update_layout(height=400)
			st.plotly_chart(fig_monthly, use_container_width=True)
		with col2:
			quarterly_data = filtered_data.copy()
			quarterly_data['Year'] = quarterly_data['Order Date'].dt.year
			quarterly_data['Quarter'] = quarterly_data['Order Date'].dt.quarter
			quarterly_grouped = quarterly_data.groupby(['Year', 'Quarter']).agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
			quarterly_grouped['Quarter_Label'] = quarterly_grouped['Year'].astype(str) + '-Q' + quarterly_grouped['Quarter'].astype(str)
			fig_quarterly = go.Figure()
			fig_quarterly.add_trace(go.Bar(x=quarterly_grouped['Quarter_Label'], y=quarterly_grouped['Sales'], name='Sales', marker_color='lightblue'))
			fig_quarterly.add_trace(go.Bar(x=quarterly_grouped['Quarter_Label'], y=quarterly_grouped['Profit'], name='Profit', marker_color='orange'))
			fig_quarterly.update_layout(title='Quarterly Sales vs Profit', barmode='group', height=400)
			st.plotly_chart(fig_quarterly, use_container_width=True)

	# Tab 2: Geographic Analysis
	with tab2:
		st.markdown("### 🗺️ Geographic Performance Analysis")
		col1, col2 = st.columns(2)
		with col1:
			region_sales = filtered_data.groupby('Region')['Sales'].sum().reset_index()
			fig_region = px.pie(region_sales, values='Sales', names='Region', title='Sales Distribution by Region', color_discrete_sequence=px.colors.qualitative.Set3)
			fig_region.update_traces(textposition='inside', textinfo='percent+label')
			st.plotly_chart(fig_region, use_container_width=True)
		with col2:
			top_states = filtered_data.groupby('State')['Sales'].sum().sort_values(ascending=False).head(10).reset_index()
			fig_states = px.bar(top_states, x='Sales', y='State', orientation='h', title='Top 10 States by Sales', color='Sales', color_continuous_scale='Blues')
			fig_states.update_layout(height=400)
			st.plotly_chart(fig_states, use_container_width=True)
		st.markdown("### 💰 Regional Profit Analysis")
		region_profit = filtered_data.groupby('Region').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
		region_profit['Profit_Margin'] = (region_profit['Profit'] / region_profit['Sales'] * 100)
		fig_margin = px.bar(region_profit, x='Region', y='Profit_Margin', title='Profit Margin by Region (%)', color='Profit_Margin', color_continuous_scale='RdYlGn')
		fig_margin.add_hline(y=15, line_dash="dash", line_color="red", annotation_text="Target 15%")
		st.plotly_chart(fig_margin, use_container_width=True)

	# Tab 3: Product Analysis
	with tab3:
		st.markdown("### 📦 Product Performance Analysis")
		col1, col2 = st.columns(2)
		with col1:
			category_data = filtered_data.groupby('Category').agg({'Sales': 'sum', 'Profit': 'sum', 'Quantity': 'sum'}).reset_index()
			fig_category = px.scatter(category_data, x='Sales', y='Profit', size='Quantity', color='Category', title='Category Performance: Sales vs Profit', hover_name='Category')
			st.plotly_chart(fig_category, use_container_width=True)
		with col2:
			subcat_sales = filtered_data.groupby('Sub-Category')['Sales'].sum().sort_values(ascending=False).head(10).reset_index()
			fig_subcat = px.bar(subcat_sales, x='Sub-Category', y='Sales', title='Top 10 Sub-Categories by Sales', color='Sales', color_continuous_scale='Viridis')
			fig_subcat.update_xaxes(tickangle=45)
			st.plotly_chart(fig_subcat, use_container_width=True)
		st.markdown("### 📊 Profitability Analysis")
		col1, col2 = st.columns(2)
		with col1:
			cat_margin = filtered_data.groupby('Category').apply(lambda x: (x['Profit'].sum() / x['Sales'].sum()) * 100).reset_index()
			cat_margin.columns = ['Category', 'Profit_Margin']
			fig_cat_margin = px.bar(cat_margin, x='Category', y='Profit_Margin', title='Profit Margin by Category (%)', color='Profit_Margin', color_continuous_scale='RdYlGn')
			fig_cat_margin.add_hline(y=0, line_dash="dash", line_color="black")
			st.plotly_chart(fig_cat_margin, use_container_width=True)
		with col2:
			filtered_data['Discount_Range'] = pd.cut(filtered_data['Discount'], bins=[0, 0.1, 0.2, 0.3, 1.0], labels=['0-10%', '10-20%', '20-30%', '30%+'])
			discount_impact = filtered_data.groupby('Discount_Range')['Profit'].mean().reset_index()
			fig_discount = px.bar(discount_impact, x='Discount_Range', y='Profit', title='Average Profit by Discount Range', color='Profit', color_continuous_scale='RdYlBu_r')
			fig_discount.add_hline(y=0, line_dash="dash", line_color="black")
			st.plotly_chart(fig_discount, use_container_width=True)

	# Tab 4: Customer Analysis
	with tab4:
		st.markdown("### 👥 Customer Analysis")
		col1, col2 = st.columns(2)
		with col1:
			segment_data = filtered_data.groupby('Segment').agg({'Sales': 'sum', 'Customer ID': 'nunique'}).reset_index()
			fig_segment = px.sunburst(filtered_data, path=['Segment', 'Category'], values='Sales', title='Sales by Customer Segment and Category')
			st.plotly_chart(fig_segment, use_container_width=True)
		with col2:
			ship_data = filtered_data.groupby('Ship Mode').agg({'Sales': 'sum', 'Order ID': 'count'}).reset_index()
			ship_data.columns = ['Ship_Mode', 'Sales', 'Orders']
			fig_ship = px.bar(ship_data, x='Ship_Mode', y=['Sales'], title='Sales by Shipping Mode', color_discrete_sequence=['lightcoral'])
			st.plotly_chart(fig_ship, use_container_width=True)
		st.markdown("### 🏆 Top Customer Analysis")
		top_customers = filtered_data.groupby('Customer Name').agg({'Sales': 'sum', 'Profit': 'sum', 'Order ID': 'count'}).sort_values('Sales', ascending=False).head(15).reset_index()
		fig_customers = px.scatter(top_customers, x='Sales', y='Profit', size='Order ID', hover_name='Customer Name', title='Top 15 Customers: Sales vs Profit', color='Order ID', color_continuous_scale='Plasma')
		st.plotly_chart(fig_customers, use_container_width=True)

	# Tab 5: Advanced Analytics
	with tab5:
		st.markdown("### 🔍 Advanced Business Analytics")
		col1, col2 = st.columns(2)
		with col1:
			correlation = filtered_data['Sales'].corr(filtered_data['Profit'])
			scatter_df = filtered_data.sample(1000) if len(filtered_data) > 1000 else filtered_data
			if HAS_STATSMODELS:
				fig_corr = px.scatter(
					scatter_df,
					x='Sales',
					y='Profit',
					color='Category',
					title=f'Sales vs Profit Correlation (r={correlation:.3f})',
					trendline='ols'
				)
			else:
				fig_corr = px.scatter(
					scatter_df,
					x='Sales',
					y='Profit',
					color='Category',
					title=f"Sales vs Profit Correlation (r={correlation:.3f}) — (install 'statsmodels' for trendline)"
				)
				st.info("Regression line disabled because 'statsmodels' is not installed. Run: `pip install statsmodels` in your app’s venv.")
			st.plotly_chart(fig_corr, use_container_width=True)
		with col2:
			ship_time = filtered_data.groupby('Ship Mode')['Days_to_Ship'].mean().reset_index()
			fig_ship_time = px.bar(ship_time, x='Ship Mode', y='Days_to_Ship', title='Average Shipping Time by Mode', color='Days_to_Ship', color_continuous_scale='Reds')
			st.plotly_chart(fig_ship_time, use_container_width=True)
		st.markdown("### 📊 Customer RFM Analysis")
		current_date = filtered_data['Order Date'].max()
		rfm_data = filtered_data.groupby('Customer ID').agg({
			'Order Date': lambda x: (current_date - x.max()).days,
			'Order ID': 'count',
			'Sales': 'sum'
		}).reset_index()
		rfm_data.columns = ['Customer ID', 'Recency', 'Frequency', 'Monetary']
		fig_rfm = px.scatter_3d(rfm_data.sample(500) if len(rfm_data) > 500 else rfm_data, x='Recency', y='Frequency', z='Monetary', title='Customer RFM Analysis (3D)', color='Monetary', size='Frequency', hover_data=['Customer ID'])
		fig_rfm.update_layout(height=600)
		st.plotly_chart(fig_rfm, use_container_width=True)

	# Footer with summary statistics
	st.markdown("---")
	st.markdown("## 📋 Executive Summary")
	col1, col2, col3 = st.columns(3)
	with col1:
		st.markdown("### 🎯 Key Insights")
		best_region = filtered_data.groupby('Region')['Sales'].sum().idxmax()
		best_category = filtered_data.groupby('Category')['Sales'].sum().idxmax()
		st.write(f"• **Best Region:** {best_region}")
		st.write(f"• **Best Category:** {best_category}")
		st.write(f"• **Profit Margin:** {profit_margin:.2f}%")
	with col2:
		st.markdown("### 📈 Performance")
		total_customers = filtered_data['Customer ID'].nunique()
		avg_shipping_days = filtered_data['Days_to_Ship'].mean()
		st.write(f"• **Total Customers:** {total_customers:,}")
		st.write(f"• **Avg Shipping:** {avg_shipping_days:.1f} days")
		st.write(f"• **Orders/Customer:** {total_orders/total_customers:.1f}")
	with col3:
		st.markdown("### ⚠️ Areas for Improvement")
		loss_orders = len(filtered_data[filtered_data['Profit'] < 0])
		loss_percentage = (loss_orders / total_orders * 100) if total_orders > 0 else 0
		high_discount = len(filtered_data[filtered_data['Discount'] > 0.3])
		st.write(f"• **Loss-making Orders:** {loss_percentage:.1f}%")
		st.write(f"• **High Discounts:** {high_discount:,} orders")
		st.write("• **Focus on:** Profit optimization")

if __name__ == "__main__":
	main()