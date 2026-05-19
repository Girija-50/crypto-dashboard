import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from cryptocmd import CmcScraper
import datetime as dt
from PIL import Image

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Advanced Crypto Dashboard",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #0f172a;
    color: white;
}

h1, h2, h3, h4 {
    color: #38bdf8;
}

.stDataFrame {
    background-color: white;
}

.sidebar .sidebar-content {
    background-color: #111827;
}

div.stButton > button {
    background-color: #38bdf8;
    color: black;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("🚀 Advanced Cryptocurrency Dashboard")

st.markdown("""
### Real-time cryptocurrency analytics dashboard  
Track prices, market trends, gainers, losers, market dominance, and historical charts.
""")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ Input Options")

currency_price_unit = st.sidebar.selectbox(
    "💱 Select Currency",
    ("USD", "BTC", "ETH")
)

limit = st.sidebar.slider(
    "📌 Number of Coins",
    10,
    100,
    50
)

chart_theme = st.sidebar.selectbox(
    "🎨 Select Chart Theme",
    ["default", "dark_background", "ggplot", "Solarize_Light2"]
)

percent_timeframe = st.sidebar.selectbox(
    "📈 Percentage Change",
    ["1h", "24h", "7d"]
)

# =========================================================
# API KEY
# =========================================================

API_KEY = "5a02544eee4049379bad033b9e6d3cfe"

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data(ttl=300)
def load_data():

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY
    }

    parameters = {
        "start": "1",
        "limit": str(limit),
        "convert": currency_price_unit
    }

    response = requests.get(url, headers=headers, params=parameters)

    data = response.json()

    crypto_data = data["data"]

    rows = []

    for coin in crypto_data:

        quote = coin["quote"][currency_price_unit]

        rows.append({
            "Name": coin["name"],
            "Symbol": coin["symbol"],
            "Price": quote["price"],
            "Market Cap": quote["market_cap"],
            "24h Volume": quote["volume_24h"],
            "1h Change": quote["percent_change_1h"],
            "24h Change": quote["percent_change_24h"],
            "7d Change": quote["percent_change_7d"]
        })

    df = pd.DataFrame(rows)

    return df

# =========================================================
# LOAD DATAFRAME
# =========================================================

try:
    df = load_data()

except Exception as e:
    st.error("Error loading CoinMarketCap data")
    st.write(e)
    st.stop()

# =========================================================
# SELECT CRYPTOS
# =========================================================

selected_coin = st.sidebar.multiselect(
    "🪙 Select Cryptocurrencies",
    df["Symbol"],
    ["BTC", "ETH", "BNB", "DOGE"]
)

filtered_df = df[df["Symbol"].isin(selected_coin)]

# =========================================================
# METRICS
# =========================================================

st.subheader("📊 Live Market Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Coins Selected",
    len(filtered_df)
)

col2.metric(
    "Highest Price",
    f"${filtered_df['Price'].max():,.2f}"
)

col3.metric(
    "Largest Market Cap",
    f"${filtered_df['Market Cap'].max():,.0f}"
)

col4.metric(
    "Highest 24h Gain",
    f"{filtered_df['24h Change'].max():.2f}%"
)

# =========================================================
# DATA TABLE
# =========================================================

st.subheader("📋 Cryptocurrency Data Table")

st.dataframe(filtered_df)

# =========================================================
# DOWNLOAD CSV
# =========================================================

csv = filtered_df.to_csv(index=False)

st.download_button(
    label="⬇️ Download CSV File",
    data=csv,
    file_name="crypto_data.csv",
    mime="text/csv"
)

# =========================================================
# CHART SETTINGS
# =========================================================

plt.style.use(chart_theme)

# =========================================================
# BAR CHART
# =========================================================

st.subheader("📈 Percentage Change Analysis")

timeframe_map = {
    "1h": "1h Change",
    "24h": "24h Change",
    "7d": "7d Change"
}

selected_timeframe = timeframe_map[percent_timeframe]

fig, ax = plt.subplots(figsize=(12, 5))

colors = ["green" if x > 0 else "red"
          for x in filtered_df[selected_timeframe]]

ax.bar(
    filtered_df["Symbol"],
    filtered_df[selected_timeframe],
    color=colors
)

ax.set_ylabel("Percent Change")

st.pyplot(fig)

# =========================================================
# PIE CHART
# =========================================================

st.subheader("🥧 Market Capitalization Share")

fig2, ax2 = plt.subplots(figsize=(8, 8))

ax2.pie(
    filtered_df["Market Cap"],
    labels=filtered_df["Symbol"],
    autopct='%1.1f%%'
)

st.pyplot(fig2)

# =========================================================
# MARKET CAP CHART
# =========================================================

st.subheader("💰 Market Capitalization")

fig3, ax3 = plt.subplots(figsize=(12, 5))

ax3.bar(
    filtered_df["Symbol"],
    filtered_df["Market Cap"],
    color="orange"
)

ax3.set_ylabel("Market Cap")

st.pyplot(fig3)

# =========================================================
# VOLUME CHART
# =========================================================

st.subheader("📦 Trading Volume")

fig4, ax4 = plt.subplots(figsize=(12, 5))

ax4.bar(
    filtered_df["Symbol"],
    filtered_df["24h Volume"],
    color="purple"
)

ax4.set_ylabel("24h Volume")

st.pyplot(fig4)

# =========================================================
# HISTORICAL PRICE GRAPH
# =========================================================

st.subheader("📉 Historical Price Analysis")

selected_crypto = st.selectbox(
    "Select Coin",
    filtered_df["Symbol"]
)

today = dt.date.today()
month_ago = today - dt.timedelta(days=30)

today = today.strftime("%d-%m-%Y")
month_ago = month_ago.strftime("%d-%m-%Y")

@st.cache_data(ttl=3600)
def get_historical_data(symbol):

    scraper = CmcScraper(symbol, month_ago, today)

    historical_df = scraper.get_dataframe()

    return historical_df

try:

    historical_df = get_historical_data(selected_crypto)

    fig5, ax5 = plt.subplots(figsize=(14, 5))

    ax5.plot(
        historical_df["Date"],
        historical_df["Close"],
        color="cyan",
        linewidth=3
    )

    ax5.set_xlabel("Date")
    ax5.set_ylabel("Closing Price")

    plt.xticks(rotation=45)

    st.pyplot(fig5)

except Exception as e:

    st.warning("Historical data unavailable")
    st.write(e)

# =========================================================
# TOP GAINERS
# =========================================================

st.subheader("🔥 Top 5 Gainers")

top_gainers = df.sort_values(
    by="24h Change",
    ascending=False
).head(5)

st.table(top_gainers[[
    "Name",
    "Symbol",
    "24h Change"
]])

# =========================================================
# TOP LOSERS
# =========================================================

st.subheader("📉 Top 5 Losers")

top_losers = df.sort_values(
    by="24h Change",
    ascending=True
).head(5)

st.table(top_losers[[
    "Name",
    "Symbol",
    "24h Change"
]])

# =========================================================
# SEARCH OPTION
# =========================================================

st.subheader("🔍 Search Cryptocurrency")

search_coin = st.text_input("Enter Coin Symbol")

if search_coin:

    result = df[df["Symbol"].str.contains(search_coin.upper())]

    st.write(result)

# =========================================================
# FOOTER
# =========================================================

st.markdown("""
---
### ✅ Features Included
✔ Live Prices  
✔ Market Cap Analysis  
✔ Pie Charts  
✔ Volume Charts  
✔ Historical Trends  
✔ Search Option  
✔ CSV Download  
✔ Top Gainers & Losers  
✔ Interactive Sidebar  
✔ Professional UI  
""")