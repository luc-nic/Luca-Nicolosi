import streamlit as st
import pandas as pd
import plotly.express as px

# I'm setting up the page configuration for a good multi-page layout experience
st.set_page_config(page_title='Time Analysis', page_icon='📅', layout='wide')

# Main Page Headers
st.title('📅 Temporal Transaction Analytics')
st.markdown('Monitor trading velocity, chronological trends, and asset distribution profiles over custom timelines.')


# Data Loading and Caching

@st.cache_data
def load_and_process_data():
    # Load raw datasets
    symbols_df = pd.read_csv('symbols.csv', sep=';')
    statement_df = pd.read_csv('account-statement-1-1-2024-12-31-2024.csv', sep=';')
    country_df = pd.read_csv('country.csv')

    # I'm renaming statement and geographic headers to prevent casing and mismatch KeyError exceptions
    statement_df = statement_df.rename(columns={'Date': 'date', 'Symbol': 'symbol', 'TransactionType': 'transaction_type', 'Unit': 'quantity'})
    country_df = country_df.rename(columns={'name': 'country'})

    # I'm standardizing textual data strings to guarantee precise inner join matching keys
    statement_df['symbol'] = statement_df['symbol'].str.strip().str.upper()
    symbols_df['symbol'] = symbols_df['symbol'].str.strip().str.upper()
    symbols_df['country'] = symbols_df['country'].str.strip()
    country_df['country'] = country_df['country'].str.strip()

    # I'm dropping rows containing missing records in analytical target fields
    statement_df = statement_df.dropna(subset=['date', 'transaction_type', 'symbol', 'quantity'])

    # Build Dim_Transaction_Type
    dim_transaction_type = pd.DataFrame({'transaction_type': sorted(statement_df['transaction_type'].unique())})
    dim_transaction_type['trans_type_id'] = dim_transaction_type.index + 1

    # Build Dim_Geography 
    dim_geography = country_df[['country', 'region', 'sub-region']].drop_duplicates().reset_index(drop=True)
    dim_geography['geography_id'] = dim_geography.index + 1
    dim_geography = dim_geography.rename(columns={'sub-region': 'sub_region'})

    # Build Dim_Symbol
    symbols_geo_mapped = symbols_df.merge(dim_geography, on='country', how='inner')
    dim_symbol = symbols_geo_mapped[['symbol', 'company_name', 'sector', 'industry', 'geography_id']].drop_duplicates().reset_index(drop=True)
    dim_symbol['symbol_id'] = dim_symbol.index + 1

    # Build Dim_Time 
    statement_df['date'] = pd.to_datetime(statement_df['date'], errors='coerce').dt.date
    statement_df = statement_df.dropna(subset=['date'])
    unique_dates = sorted(statement_df['date'].unique())

    dim_time = pd.DataFrame({'date': unique_dates})
    dim_time['date'] = pd.to_datetime(dim_time['date'])
    dim_time['day_of_week'] = dim_time['date'].dt.day_name()
    dim_time['month'] = dim_time['date'].dt.month
    dim_time['quarter'] = dim_time['date'].dt.quarter
    dim_time['year'] = dim_time['date'].dt.year
    dim_time['time_id'] = dim_time.index + 1

    statement_df['date'] = pd.to_datetime(statement_df['date'])

    # I'm assembling the central Fact Table by mapping natural elements to surrogate keys
    fact_stage = statement_df.merge(dim_time, on='date', how='inner') \
                              .merge(dim_transaction_type, on='transaction_type', how='inner') \
                              .merge(dim_symbol, on='symbol', how='inner')
    
    fact_transactions = fact_stage[['time_id', 'symbol_id', 'geography_id', 'trans_type_id', 'quantity']]

    return fact_transactions, dim_time, dim_symbol, dim_transaction_type

# I'm executing the processed memory block
fact_transactions, dim_time, dim_symbol, dim_transaction_type = load_and_process_data()

# I'm building unified flat master dataframe for hardware-accelerated charting performance
master_df = fact_transactions.merge(dim_time, on='time_id', how='inner') \
                             .merge(dim_symbol, on='symbol_id', how='inner') \
                             .merge(dim_transaction_type, on='trans_type_id', how='inner')

# Theme Branding and Palette Definitions

custom_teal_palette = ["#008080", "#20B2AA", "#48D1CC", "#00CED1", "#00FFFF"]


# Interactive Filters (Sidebar Date Range Selector)

st.sidebar.header('📅 Timeline Boundaries')

min_calendar_date = master_df['date'].min().date()
max_calendar_date = master_df['date'].max().date()

# Dynamic slider/calendar window selector widget

selected_range = st.sidebar.date_input(
    label='Set Interactive Date Filter:',
    value=(min_calendar_date, max_calendar_date),
    min_value=min_calendar_date,
    max_value=max_calendar_date
)

# I'm filtering database reactively when full range bounds are provided by user
if len(selected_range) == 2:
    start_date, end_date = selected_range
    filtered_df = master_df[(master_df['date'].dt.date >= start_date) & (master_df['date'].dt.date <= end_date)]
else:
    filtered_df = master_df


# High-Performance Interactive Plotly Visualization

# Line Chart: Traded units/orders frequency over time
st.subheader('📈 Chronological Portfolio Trading Velocity')
# FIXED: Unified spelling error on 'Transaction Frequency' column link keys
timeline_data = filtered_df.groupby('date').size().reset_index(name='Transaction Frequency')

fig_timeline = px.line(
    timeline_data, x='date', y='Transaction Frequency', 
    template='plotly_white', color_discrete_sequence=[custom_teal_palette[0]]
)

fig_timeline.update_layout(xaxis_title=None, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_timeline, use_container_width=True)

st.markdown('---')

# Layout distributions columns for metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('### 🥇 Top 3 Traded Symbols')
    # I'm grouping and aggregating top assets
    top_3_symbols = filtered_df.groupby('symbol').size().reset_index(name='Orders') \
                               .sort_values(by='Orders', ascending=False).head(3)
    
    fig_sym = px.bar(
        top_3_symbols, x='symbol', y='Orders',
        template='plotly_white', color_discrete_sequence=[custom_teal_palette[1]]
    )

    fig_sym.update_layout(xaxis_title=None, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_sym, use_container_width=True)

with col2:
    st.markdown('### 🏢 Top 5 Corporate Sectors')
    # I'm grouping and aggregating top market sectors
    top_5_sectors = filtered_df.groupby('sector').size().reset_index(name='Orders') \
                               .sort_values(by='Orders', ascending=False).head(5)
    
    fig_sec = px.bar(
        top_5_sectors, x='sector', y='Orders', 
        template="plotly_white", color_discrete_sequence=[custom_teal_palette[2]]
    )
    fig_sec.update_layout(xaxis_title=None, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_sec, use_container_width=True)

with col3:
    st.markdown("### 🏭 Top 5 Industry Niches")
    # Group and aggregate precise industries
    top_5_industries = filtered_df.groupby('industry').size().reset_index(name='Orders') \
                                 .sort_values(by='Orders', ascending=False).head(5)
    
    fig_ind = px.bar(
        top_5_industries, x='industry', y='Orders', 
        template="plotly_white", color_discrete_sequence=[custom_teal_palette[3]]
    )
    fig_ind.update_layout(xaxis_title=None, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_ind, use_container_width=True)

    