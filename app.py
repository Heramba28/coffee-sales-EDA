import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="Coffee Shop Sales Dashboard", layout="wide")

# Load data with caching
@st.cache_data
def load_data():
    df = pd.read_excel('Coffee Shop Sales.xlsx')
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['day'] = df['transaction_date'].dt.day
    df['month'] = df['transaction_date'].dt.month_name()
    df['year'] = df['transaction_date'].dt.year
    return df

# Load data
df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")
store = st.sidebar.multiselect("📍 Store Location", df['store_location'].unique())
category = st.sidebar.multiselect("🧃 Product Category", df['product_category'].unique())
ptype = st.sidebar.multiselect("📦 Product Type", df['product_type'].unique())
date_range = st.sidebar.date_input("🗓️ Date Range", [df['transaction_date'].min(), df['transaction_date'].max()])

# Apply filters
filtered = df.copy()
if store:
    filtered = filtered[filtered['store_location'].isin(store)]
if category:
    filtered = filtered[filtered['product_category'].isin(category)]
if ptype:
    filtered = filtered[filtered['product_type'].isin(ptype)]
if len(date_range) == 2:
    filtered = filtered[
        (filtered['transaction_date'] >= pd.to_datetime(date_range[0])) &
        (filtered['transaction_date'] <= pd.to_datetime(date_range[1]))
    ]
elif len(date_range) == 1:
    filtered = filtered[filtered['transaction_date'] >= pd.to_datetime(date_range[0])]

# KPIs
st.title("☕ Coffee Shop Sales Dashboard")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Sales", f"${filtered['unit_price'].sum():,.2f}")
col2.metric("🧾 Total Transactions", f"{filtered.shape[0]}")
col3.metric("📈 Avg. Unit Price", f"${filtered['unit_price'].mean():.2f}")
col4.metric("🏆 Top Product", filtered['product_type'].mode()[0] if not filtered.empty else "N/A")

# Sales over time
st.subheader("📈 Sales Over Time")
chart_type = st.radio("Choose chart type:", ["Line Chart", "Bar Chart"], horizontal=True)
sales_over_time = filtered.groupby('transaction_date')['unit_price'].sum()
if chart_type == "Line Chart":
    st.line_chart(sales_over_time)
else:
    st.bar_chart(sales_over_time)

# Sales by store location
st.subheader("🏬 Sales by Store Location")
store_sales = filtered.groupby('store_location')['unit_price'].sum().sort_values(ascending=False)
fig1, ax1 = plt.subplots()
sns.barplot(x=store_sales.values, y=store_sales.index, palette='Blues_r', ax=ax1)
ax1.set_xlabel("Total Sales")
ax1.set_ylabel("Store Location")
ax1.set_title("Sales by Store Location")
st.pyplot(fig1)

# Top N product types
st.subheader("📦 Top N Product Types by Transactions")
top_n = st.slider("Select number of top products", min_value=3, max_value=15, value=5)
top_products = filtered['product_type'].value_counts().head(top_n)
fig2, ax2 = plt.subplots()
sns.barplot(x=top_products.values, y=top_products.index, palette='Greens_r', ax=ax2)
ax2.set_xlabel("Transaction Count")
ax2.set_title("Top Product Types")
st.pyplot(fig2)

# Product category share
st.subheader("📊 Product Category Distribution")
fig3, ax3 = plt.subplots()
sns.countplot(data=filtered, x='product_category', palette='Pastel1', order=filtered['product_category'].value_counts().index, ax=ax3)
ax3.set_title("Product Category Share")
ax3.set_xlabel("Category")
ax3.set_ylabel("Count")
plt.xticks(rotation=45)
st.pyplot(fig3)

# Heatmap
st.subheader("🔥 Heatmap: Product Type vs Store Location (Transactions)")
pivot = filtered.pivot_table(index='product_type', columns='store_location', values='transaction_qty', aggfunc='sum', fill_value=0)
fig4, ax4 = plt.subplots(figsize=(12, 8))
sns.heatmap(pivot, annot=True, fmt='.0f', cmap='viridis', linewidths=0.5, ax=ax4)
ax4.set_title("Transaction Quantity by Product and Store")
st.pyplot(fig4)

# Download button
st.subheader("📥 Download Filtered Data")
st.download_button("Download as CSV", filtered.to_csv(index=False), file_name="filtered_data.csv")

# Show data
st.subheader("🗃️ Filtered Data")
st.dataframe(filtered, use_container_width=True)
