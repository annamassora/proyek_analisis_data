import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style="dark")

dataset_df = pd.read_csv("dataset.csv")
# dataset_df.info()
# print(dataset_df.loc[0, "order_approved_at"])

#   create_daily_orders_df() digunakan untuk menyiapkan daily_orders_df
def create_daily_orders_df(dataset_df):
    daily_orders_df = dataset_df.resample(rule="D", on="order_approved_at").agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    daily_orders_df.fillna(0, inplace=True)
    
    return daily_orders_df

#   create_sum_order_items_df() bertanggung jawab untuk menyiapkan sum_orders_items_df
def create_sum_order_items_df(dataset_df):
    sum_order_items_df = dataset_df.groupby("product_category_name")["order_id"].nunique().sort_values(ascending=False).reset_index()

    return sum_order_items_df

#   create_bystate_df() digunakan untuk menyiapkan bystate_df
def create_bystate_df(dataset_df):
    bystate_df = dataset_df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bystate_df

#   create_bycity_df() digunakan untuk menyiapkan bycity_df
def create_bycity_df(dataset_df):
    bycity_df = dataset_df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bycity_df

# create_top_purchase_by_city_df untuk menyiapkan top_purchase_by_city
def create_top_purchase_by_city_df(dataset_df):
    top_purchase_by_city = dataset_df.groupby("customer_city")["price"].sum().reset_index()
    top_purchase_by_city = top_purchase_by_city.sort_values(by="price", ascending=False).head(10)
    return top_purchase_by_city

# create_top_purchase_by_state_df untuk menyiapkan top_purchase_by_state
def create_top_purchase_by_state_df(dataset_df):
    top_purchase_by_state = dataset_df.groupby("customer_state")["price"].sum().reset_index()
    top_purchase_by_state = top_purchase_by_state.sort_values(by="price", ascending=False).head(10)
    return top_purchase_by_state

# create_monthly_trend_df untuk menyiapkan monthly_trend_df
def create_monthly_trend_df(dataset_df):
    monthly_trend_df = dataset_df.resample("M", on="order_approved_at").agg({
        "order_id": "nunique",  
        "price": "sum"  
    }).reset_index()
    
    monthly_trend_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)

    monthly_trend_df["month_year"] = monthly_trend_df["order_approved_at"].dt.strftime('%Y-%m')
    
    return monthly_trend_df[["month_year", "order_count", "revenue"]]

#   create_rfm_df() bertanggung jawab untuk menghasilkan rfm_df
def create_rfm_df(dataset_df):
    rfm_df = dataset_df.groupby(by="customer_id", as_index=False).agg({
        "order_approved_at": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "price": "sum"
    })
    
    rfm_df.columns = ["customer_id", "max_order_approved", "frequency", "monetary"]
    
    rfm_df["max_order_approved"] = rfm_df["max_order_approved"].dt.date
    recent_date = dataset_df["order_approved_at"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_approved"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_approved", axis=1, inplace=True)
    
    return rfm_df

datetime_columns = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "estimated_delivery_time", "shipping_limit_date"]
dataset_df.sort_values(by="order_approved_at", inplace=True)
dataset_df.reset_index(inplace=True)
 
for column in datetime_columns:
    dataset_df[column] = pd.to_datetime(dataset_df[column])
    
#   Membuat Komponen Filter
min_date = dataset_df["order_approved_at"].min()
max_date = dataset_df["order_approved_at"].max()
six_months_ago = max_date - pd.DateOffset(months=6)

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("e-commerce.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Rentang Waktu",min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = dataset_df[(dataset_df["order_approved_at"] >= str(start_date)) & 
                 (dataset_df["order_approved_at"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bystate_df = create_bystate_df(main_df)
bycity_df = create_bycity_df(main_df)
top_purchase_by_city_df = create_top_purchase_by_city_df(main_df)
top_purchase_by_state_df = create_top_purchase_by_state_df(main_df)
rfm_df = create_rfm_df(main_df)

recent_six_months_df = dataset_df[(dataset_df["order_approved_at"] >= six_months_ago) & 
                                  (dataset_df["order_approved_at"] <= max_date)]

monthly_trend_df = create_monthly_trend_df(recent_six_months_df)


st.header("E-commerce Dashboard :sparkles:")



''' DAILY ORDER '''
st.subheader("Daily Orders")
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o", 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="y", labelsize=20)
ax.tick_params(axis="x", labelsize=15)
 
st.pyplot(fig)



''' Best & Worst Performing Product '''
st.subheader("Best & Worst Performing Product")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="order_id", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel("None")
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="order_id", y="product_category_name", data=sum_order_items_df.sort_values(by="order_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)



''' Customer Demographics '''
st.subheader("Customer Demographics")
 
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    
    colors = ["#D3D3D3", "#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
    sns.barplot(
        y="customer_count", 
        x="customer_city",
        data=bycity_df.sort_values(by="customer_city", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Customer by Cities", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
 
    sns.barplot(
    x="customer_count", 
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    palette=colors,
    ax=ax
)
    ax.set_title("Number of Customer by States", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)



''' Top Purchase by City and State '''
st.subheader("Top Purchase by City and State")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x="price", 
        y="customer_city", 
        data=top_purchase_by_city_df, 
        palette="Blues_r", 
        ax=ax
    )
    ax.set_title("Top 10 Purchase Cities", fontsize=16)
    ax.set_xlabel("Total Purchase", fontsize=12)
    ax.set_ylabel("City", fontsize=12)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x="price", 
        y="customer_state", 
        data=top_purchase_by_state_df, 
        palette="Reds_r", 
        ax=ax
    )
    ax.set_title("Top 10 Purchase States", fontsize=16)
    ax.set_xlabel("Total Purchase", fontsize=12)
    ax.set_ylabel("State", fontsize=12)
    st.pyplot(fig)



''' Purchase Trend for the Last 6 Months '''
st.header("Purchase Trend for the Last 6 Months")

# Display trend visualization
st.subheader("Order Count Trend for the Last 6 Months")
plt.figure(figsize=(10, 5))
plt.plot(monthly_trend_df["month_year"], monthly_trend_df["order_count"], marker="o", linewidth=2, color="#72BCD4")
plt.title("Order Count Trend for the Last 6 Months", fontsize=15)
plt.xlabel("Month", fontsize=12)
plt.ylabel("Order Count", fontsize=12)
plt.xticks(rotation=45)
plt.grid(linestyle="--", linewidth=0.5)
st.pyplot(plt)

st.subheader("Revenue Trend for the Last 6 Months")
plt.figure(figsize=(10, 5))
plt.plot(monthly_trend_df["month_year"], monthly_trend_df["revenue"], marker="o", linewidth=2, color="#72BCD4")
plt.title("Revenue Trend for the Last 6 Months", fontsize=15)
plt.xlabel("Month", fontsize=12)
plt.ylabel("Revenue", fontsize=12)
plt.xticks(rotation=45)
plt.grid(linestyle="--", linewidth=0.5)
st.pyplot(plt)



''' Best Customer Based on RFM Parameters '''
st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)
 
st.caption("Copyright (c) Anna 2025")