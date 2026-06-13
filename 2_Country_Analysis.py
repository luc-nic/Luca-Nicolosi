import streamlit as st
import pandas as pd
import plotly.express as px

# I'm setting up the page configuration for a good multi-page layout experience
st.set_page_config(page_title="Country Analysis", page_icon="🌍", layout="wide")

# Main Page Headers
st.title("🌍 Geographic Market Analytics")
st.markdown("Deep-dive into specific global markets to analyze asset concentration and trade distributions.")

# Data Loading 
# I'm loading raw datasets directly from the root folder
symbols_df = pd.read_csv('symbols.csv', sep=';')
statement_df = pd.read_csv('account-statement-1-1-2024-12-31-2024.csv', sep=';')
country_df = pd.read_csv('country.csv')

# Header standardization to prevent casing and mismatch KeyError exceptions
statement_df = statement_df.rename(columns={'Date': 'date', 'Symbol': 'symbol', 'TransactionType': 'transaction_type', 'Unit': 'quantity'})
country_df = country_df.rename(columns={'name': 'country'})

# Text cleaning to guarantee precise inner join matching keys
statement_df['symbol'] = statement_df['symbol'].str.strip().str.upper()
symbols_df['symbol'] = symbols_df['symbol'].str.strip().str.upper()
symbols_df['country'] = symbols_df['country'].str.strip()
country_df['country'] = country_df['country'].str.strip()

# Drop potential rows containing missing records in analytical target fields
statement_df = statement_df.dropna(subset=['date', 'transaction_type', 'symbol', 'quantity'])

# Build Dimensions inline
dim_transaction_type = pd.DataFrame({'transaction_type': sorted(statement_df['transaction_type'].unique())})
dim_transaction_type['trans_type_id'] = dim_transaction_type.index + 1

dim_geography = country_df[['country', 'region', 'sub-region']].drop_duplicates().reset_index(drop=True)
dim_geography['geography_id'] = dim_geography.index + 1
dim_geography = dim_geography.rename(columns={'sub-region': 'sub_region'})

symbols_geo_mapped = symbols_df.merge(dim_geography, on='country', how='inner')
dim_symbol = symbols_geo_mapped[['symbol', 'company_name', 'sector', 'industry', 'geography_id']].drop_duplicates().reset_index(drop=True)
dim_symbol['symbol_id'] = dim_symbol.index + 1

statement_df['date'] = pd.to_datetime(statement_df['date'], errors='coerce').dt.date
statement_df = statement_df.dropna(subset=['date'])
unique_dates = sorted(statement_df['date'].unique())

dim_time = pd.DataFrame({'date': unique_dates})
dim_time['date'] = pd.to_datetime(dim_time['date'])
dim_time['year'] = dim_time['date'].dt.year
dim_time['time_id'] = dim_time.index + 1

statement_df['date'] = pd.to_datetime(statement_df['date'])

# Assemble unified flat master dataframe
fact_stage = statement_df.merge(dim_time, on='date', how='inner') \
                          .merge(dim_transaction_type, on='transaction_type', how='inner') \
                          .merge(dim_symbol, on='symbol', how='inner')

country_master_df = fact_stage.copy()

# Filter context strictly for the year 2024 as requested by the task requirements
country_master_df = country_master_df[country_master_df['year'] == 2024]

# Palette Setup
custom_teal_palette = ["#008080", "#20B2AA", "#48D1CC", "#00CED1", "#00FFFF"]

# Interactive Filters (Sidebar Market Selector)

# Dynamic dropdown for selecting the country based on the absolute master list from country.csv
all_possible_countries = sorted(country_df['country'].unique())
selected_country = st.sidebar.selectbox("Select Country Target:", all_possible_countries)

# I'm applying reactive filter based on user selection
filtered_country_df = country_master_df[country_master_df['country'] == selected_country]

# Main Dashboard Interactive Visualization and Empty State Handling
st.subheader(f'Analysis Summary for Market: {selected_country}')

# If no transaction exist for the selected country, display an appropriate message
if filtered_country_df.empty:
    st.warning(f'⚠️ No portfolio transaction ledger entries found for {selected_country} during the calendar year 2024.')
else:
    # Line Chart representing the trend of total transaction (BUY + SELL) during 2024
    st.markdown('### 📈 Chronological Transaction Trend (BUY + SELL) inside 2024')
    trend_data = filtered_country_df.groupby('date').size().reset_index(name='Total Transactions')

    fig_trend = px.line(trend_data, x='date', y='Total Transactions', template='plotly_white', color_discrete_sequence=[custom_teal_palette[0]])

    fig_trend.update_layout(xaxis_title=None, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown('---')

    # I'm defining a layout splitted in two columns for BUY and SELL industry breakdowns
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown('### 📥 Top Industries by BUY Transactions')
        # I'm filtering context for BUY operations
        buy_data = filtered_country_df[filtered_country_df['transaction_type'] == 'BUY']

        if buy_data.empty:
            st.info('No BUY transactions recorded for this market context.')
        else:
            top_buy_industries = buy_data.groupby('industry').size().reset_index(name='BUY Count') \
                                         .sort_values(by='BUY Count', ascending=False)
            
            fig_buy = px.bar(top_buy_industries, x='industry', y='BUY Count', template='plotly_white', color_discrete_sequence=[custom_teal_palette[1]])

            fig_buy.update_layout(xaxis_title=None, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_buy, use_container_width=True)
    
    with right_col:
        st.markdown("### 📤 Top Industries by SELL Transactions")
        # I'm filtering context for SELL operations
        sell_data = filtered_country_df[filtered_country_df['transaction_type'] == 'SELL']
        
        if sell_data.empty:
            st.info("No SELL transactions recorded for this market context.")
        else:
            top_sell_industries = sell_data.groupby('industry').size().reset_index(name='SELL Count') \
                                           .sort_values(by='SELL Count', ascending=False)
            
            fig_sell = px.bar(top_sell_industries, x='industry', y='SELL Count', template="plotly_white", color_discrete_sequence=[custom_teal_palette[2]])
            
            fig_sell.update_layout(xaxis_title=None, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_sell, use_container_width=True)