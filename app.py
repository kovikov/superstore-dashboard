 
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
	page_title="SuperStore Analytics Dashboard",
	page_icon="🏪",
	layout="wide",
	initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
	.main-header {
		font-size: 3rem;
		color: #1f77b4;
		text-align: center;
		margin-bottom: 2rem;
		text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
	}
	.metric-card {
		background-color: #f0f2f6;
		padding: 1rem;
		border-radius: 10px;
		margin: 0.5rem;
		border-left: 5px solid #1f77b4;
	}
	.sidebar .sidebar-content {
		background-color: #f8f9fa;
	}
	.stSelectbox > div > div > div {
		background-color: white;
	}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
	"""Load and preprocess the SuperStore data"""
	try:
		# Load all sheets
		orders = pd.read_excel('SuperStore Data.xlsx', sheet_name='Orders', engine='openpyxl')
		locations = pd.read_excel('SuperStore Data.xlsx', sheet_name='Location', engine='openpyxl')
		customers = pd.read_excel('SuperStore Data.xlsx', sheet_name='Customers', engine='openpyxl')
		products = pd.read_excel('SuperStore Data.xlsx', sheet_name='Products', engine='openpyxl')
		salesteam = pd.read_excel('SuperStore Data.xlsx', sheet_name='SalesTeam', engine='openpyxl')
		# Data preprocessing
		orders['Order Date'] = pd.to_datetime(orders['Order Date'])
		orders['Ship Date'] = pd.to_datetime(orders['Ship Date'])
		orders['Year'] = orders['Order Date'].dt.year
		orders['Month'] = orders['Order Date'].dt.month
		orders['Quarter'] = orders['Order Date'].dt.quarter
		orders['Month_Name'] = orders['Order Date'].dt.strftime('%B')
		# Merge all datasets
		data = orders.copy()
		data = data.merge(locations, on='Location ID', how='left')
		data = data.merge(customers, on='Customer ID', how='left')
		data = data.merge(products, on='Product ID', how='left')
		data = data.merge(salesteam, on='Sales Rep', how='left')
		# Calculate additional metrics
		data['Profit_Margin'] = (data['Profit'] / data['Sales']) * 100
		data['Days_to_Ship'] = (data['Ship Date'] - data['Order Date']).dt.days
		return data
	except FileNotFoundError:
		st.error("📁 SuperStore Data.xlsx not found! Please make sure the file is in the same directory as this app.")
		st.stop()
	except Exception as e:
		st.error(f"❌ Error loading data: {str(e)}")
		st.stop()

def main():
	# Load data
	data = load_data()
    
	# Main header
	st.markdown('<h1 class="main-header">🏪 SuperStore Analytics Dashboard</h1>', unsafe_allow_html=True)
	st.markdown("---")
    
	# Sidebar filters
	st.sidebar.image("https://via.placeholder.com/300x100/1f77b4/white?text=SuperStore", width=280)
	st.sidebar.markdown("## 🔍 Filters & Controls")
    
	# Date range filter
	date_range = st.sidebar.date_input(
		"📅 Select Date Range",
		value=[data['Order Date'].min().date(), data['Order Date'].max().date()],
		min_value=data['Order Date'].min().date(),
		max_value=data['Order Date'].max().date()
	)
    
	# Region filter
	regions = st.sidebar.multiselect(
		"🌎 Select Regions",
		options=data['Region'].unique(),
		default=data['Region'].unique()
	)
    
	# Category filter
	categories = st.sidebar.multiselect(
		"📦 Select Categories",
		options=data['Category'].unique(),
		default=data['Category'].unique()
	)
    
	# Customer segment filter
	segments = st.sidebar.multiselect(
		"👥 Select Customer Segments",
		options=data['Segment'].unique(),
		default=data['Segment'].unique()
	)
    
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
			# Monthly sales trend
			monthly_sales = filtered_data.groupby(filtered_data['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
			monthly_sales['Order Date'] = monthly_sales['Order Date'].astype(str)
            
			fig_monthly = px.line(
				monthly_sales, 
				x='Order Date', 
				y='Sales',
				title='Monthly Sales Trend',
				markers=True,
				line_shape='spline'
			)
			fig_monthly.update_layout(height=400)
			st.plotly_chart(fig_monthly, use_container_width=True)
        
		with col2:
			# Quarterly performance
			quarterly_data = filtered_data.groupby(['Year', 'Quarter']).agg({
				'Sales': 'sum',
				'Profit': 'sum'
			}).reset_index()
			quarterly_data['Quarter_Label'] = quarterly_data['Year'].astype(str) + '-Q' + quarterly_data['Quarter'].astype(str)
            
			fig_quarterly = go.Figure()
			fig_quarterly.add_trace(go.Bar(
				x=quarterly_data['Quarter_Label'],
				y=quarterly_data['Sales'],
				name='Sales',
				marker_color='lightblue'
			))
			fig_quarterly.add_trace(go.Bar(
				x=quarterly_data['Quarter_Label'],
				y=quarterly_data['Profit'],
				name='Profit',
				marker_color='orange'
			))
			fig_quarterly.update_layout(
				title='Quarterly Sales vs Profit',
				barmode='group',
				height=400
			)
			st.plotly_chart(fig_quarterly, use_container_width=True)
        
		# Year-over-year growth
		st.markdown("### 📊 Year-over-Year Performance")
		yearly_data = filtered_data.groupby('Year').agg({
			'Sales': 'sum',
			'Profit': 'sum',
			'Order ID': 'count'
		}).reset_index()
        
		fig_yearly = make_subplots(specs=[[{"secondary_y": True}]])
		fig_yearly.add_trace(
			go.Bar(x=yearly_data['Year'], y=yearly_data['Sales'], name="Sales", marker_color='skyblue'),
			secondary_y=False,
		)
		fig_yearly.add_trace(
			go.Scatter(x=yearly_data['Year'], y=yearly_data['Order ID'], mode='lines+markers', name="Orders", line=dict(color='red', width=3)),
			secondary_y=True,
		)
		fig_yearly.update_layout(title_text="Annual Sales and Order Volume")
		fig_yearly.update_yaxes(title_text="Sales ($)", secondary_y=False)
		fig_yearly.update_yaxes(title_text="Number of Orders", secondary_y=True)
        
		st.plotly_chart(fig_yearly, use_container_width=True)
    
	# Tab 2: Geographic Analysis
	with tab2:
		st.markdown("### 🗺️ Geographic Performance Analysis")
        
		col1, col2 = st.columns(2)
        
		with col1:
			# Sales by region
			region_sales = filtered_data.groupby('Region')['Sales'].sum().reset_index()
			fig_region = px.pie(
				region_sales,
				values='Sales',
				names='Region',
				title='Sales Distribution by Region',
				color_discrete_sequence=px.colors.qualitative.Set3
			)
			fig_region.update_traces(textposition='inside', textinfo='percent+label')
			st.plotly_chart(fig_region, use_container_width=True)
        
		with col2:
			# Top states
			top_states = filtered_data.groupby('State')['Sales'].sum().sort_values(ascending=False).head(10).reset_index()
			fig_states = px.bar(
				top_states,
				x='Sales',
				y='State',
				orientation='h',
				title='Top 10 States by Sales',
				color='Sales',
				color_continuous_scale='Blues'
			)
			fig_states.update_layout(height=400)
			st.plotly_chart(fig_states, use_container_width=True)
        
		# Profit margin by region
		st.markdown("### 💰 Regional Profit Analysis")
		region_profit = filtered_data.groupby('Region').agg({
			'Sales': 'sum',
			'Profit': 'sum'
		}).reset_index()
		region_profit['Profit_Margin'] = (region_profit['Profit'] / region_profit['Sales'] * 100)
        
		fig_margin = px.bar(
			region_profit,
			x='Region',
			y='Profit_Margin',
			title='Profit Margin by Region (%)',
			color='Profit_Margin',
			color_continuous_scale='RdYlGn'
		)
		fig_margin.add_hline(y=15, line_dash="dash", line_color="red", annotation_text="Target 15%")
		st.plotly_chart(fig_margin, use_container_width=True)
    
	# Tab 3: Product Analysis
	with tab3:
		st.markdown("### 📦 Product Performance Analysis")
        
		col1, col2 = st.columns(2)
        
		with col1:
			# Category performance
			category_data = filtered_data.groupby('Category').agg({
				'Sales': 'sum',
				'Profit': 'sum',
				'Quantity': 'sum'
			}).reset_index()
            
			fig_category = px.scatter(
				category_data,
				x='Sales',
				y='Profit',
				size='Quantity',
				color='Category',
				title='Category Performance: Sales vs Profit',
				hover_name='Category'
			)
			st.plotly_chart(fig_category, use_container_width=True)
        
		with col2:
			# Sub-category top performers
			subcat_sales = filtered_data.groupby('Sub-Category')['Sales'].sum().sort_values(ascending=False).head(10).reset_index()
			fig_subcat = px.bar(
				subcat_sales,
				x='Sub-Category',
				y='Sales',
				title='Top 10 Sub-Categories by Sales',
				color='Sales',
				color_continuous_scale='Viridis'
			)
			fig_subcat.update_xaxes(tickangle=45)
			st.plotly_chart(fig_subcat, use_container_width=True)
        
		# Profit margin analysis
		st.markdown("### 📊 Profitability Analysis")
        
		col1, col2 = st.columns(2)
        
		with col1:
			# Category profit margins
			cat_margin = filtered_data.groupby('Category').apply(
				lambda x: (x['Profit'].sum() / x['Sales'].sum()) * 100
			).reset_index()
			cat_margin.columns = ['Category', 'Profit_Margin']
            
			fig_cat_margin = px.bar(
				cat_margin,
				x='Category',
				y='Profit_Margin',
				title='Profit Margin by Category (%)',
				color='Profit_Margin',
				color_continuous_scale='RdYlGn'
			)
			fig_cat_margin.add_hline(y=0, line_dash="dash", line_color="black")
			st.plotly_chart(fig_cat_margin, use_container_width=True)
        
		with col2:
			# Discount impact analysis
			filtered_data['Discount_Range'] = pd.cut(
				filtered_data['Discount'],
				bins=[0, 0.1, 0.2, 0.3, 1.0],
				labels=['0-10%', '10-20%', '20-30%', '30%+']
			)
			discount_impact = filtered_data.groupby('Discount_Range')['Profit'].mean().reset_index()
            
			fig_discount = px.bar(
				discount_impact,
				x='Discount_Range',
				y='Profit',
				title='Average Profit by Discount Range',
				color='Profit',
				color_continuous_scale='RdYlBu_r'
			)
			fig_discount.add_hline(y=0, line_dash="dash", line_color="black")
			st.plotly_chart(fig_discount, use_container_width=True)
    
	# Tab 4: Customer Analysis
	with tab4:
		st.markdown("### 👥 Customer Analysis")
        
		col1, col2 = st.columns(2)
        
		with col1:
			# Customer segment distribution
			segment_data = filtered_data.groupby('Segment').agg({
				'Sales': 'sum',
				'Customer ID': 'nunique'
			}).reset_index()
            
			fig_segment = px.sunburst(
				filtered_data,
				path=['Segment', 'Category'],
				values='Sales',
				title='Sales by Customer Segment and Category'
			)
			st.plotly_chart(fig_segment, use_container_width=True)
        
		with col2:
			# Shipping mode analysis
			ship_data = filtered_data.groupby('Ship Mode').agg({
				'Sales': 'sum',
				'Order ID': 'count'
			}).reset_index()
			ship_data.columns = ['Ship_Mode', 'Sales', 'Orders']
            
			fig_ship = px.bar(
				ship_data,
				x='Ship_Mode',
				y=['Sales'],
				title='Sales by Shipping Mode',
				color_discrete_sequence=['lightcoral']
			)
			st.plotly_chart(fig_ship, use_container_width=True)
        
		# Top customers analysis
		st.markdown("### 🏆 Top Customer Analysis")
		top_customers = filtered_data.groupby('Customer Name').agg({
			'Sales': 'sum',
			'Profit': 'sum',
			'Order ID': 'count'
		}).sort_values('Sales', ascending=False).head(15).reset_index()
        
		fig_customers = px.scatter(
			top_customers,
			x='Sales',
			y='Profit',
			size='Order ID',
			hover_name='Customer Name',
			title='Top 15 Customers: Sales vs Profit',
			color='Order ID',
			color_continuous_scale='Plasma'
		)
		st.plotly_chart(fig_customers, use_container_width=True)
    
	# Tab 5: Advanced Analytics
	with tab5:
		st.markdown("### 🔍 Advanced Business Analytics")
        
		col1, col2 = st.columns(2)
        
		with col1:
			# Sales vs Profit correlation
			correlation = filtered_data['Sales'].corr(filtered_data['Profit'])
            
			fig_corr = px.scatter(
				filtered_data.sample(1000) if len(filtered_data) > 1000 else filtered_data,
				x='Sales',
				y='Profit',
				color='Category',
				title=f'Sales vs Profit Correlation (r={correlation:.3f})',
				trendline='ols'
			)
			st.plotly_chart(fig_corr, use_container_width=True)
        
		with col2:
			# Shipping time analysis
			ship_time = filtered_data.groupby('Ship Mode')['Days_to_Ship'].mean().reset_index()
            
			fig_ship_time = px.bar(
				ship_time,
				x='Ship Mode',
				y='Days_to_Ship',
				title='Average Shipping Time by Mode',
				color='Days_to_Ship',
				color_continuous_scale='Reds'
			)
			st.plotly_chart(fig_ship_time, use_container_width=True)
        
		# RFM Analysis
		st.markdown("### 📊 Customer RFM Analysis")
        
		# Calculate RFM metrics
		current_date = filtered_data['Order Date'].max()
		rfm_data = filtered_data.groupby('Customer ID').agg({
			'Order Date': lambda x: (current_date - x.max()).days,  # Recency
			'Order ID': 'count',  # Frequency
			'Sales': 'sum'  # Monetary
		}).reset_index()
        
		rfm_data.columns = ['Customer ID', 'Recency', 'Frequency', 'Monetary']
        
		# Create RFM visualization
		fig_rfm = px.scatter_3d(
			rfm_data.sample(500) if len(rfm_data) > 500 else rfm_data,
			x='Recency',
			y='Frequency',
			z='Monetary',
			title='Customer RFM Analysis (3D)',
			color='Monetary',
			size='Frequency',
			hover_data=['Customer ID']
		)
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
		st.write(f"• **Focus on:** Profit optimization")

if __name__ == "__main__":
	main()
