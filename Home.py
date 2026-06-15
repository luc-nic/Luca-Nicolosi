import streamlit as st

# I'm setting up page configuration for a professional look
st.set_page_config(page_title= 'Financial Transaction Analytics Dashboard', page_icon= '📊', layout= 'wide') 

# I'm setting the main title and subtitle
st.title('Financial Transactions Portfolio Dashboard')
st.subheader('Enterprise Business Intelligence System')

st.markdown('---')

# Welcome and Introduction Section
st.markdown("""
### Welcome to the Interactive Financial Analytics Platform
This multi-page Streamlit application delivers comprehensive auditing, monitoring, and trend analysis 
for stock portfolio transactions executed throughout the calendar year 2024. 

The application is fully backed by a scalable **Dimensional Star Schema Model**, transforming raw transaction 
statement logs into clean, aggregate-ready business insights.
""")

# Key Features Callout Box
st.info("""
**Navigate through the system using the sidebar on the left:**
* **Time Analysis:** Track trading velocity, transaction trends, and dominant macro sectors across different timelines and custom date ranges.
* **Country Analysis:** Deep-dive into specific geographic markets to investigate asset concentration, specific localized industry trends, and trade buy/sell distributions.
""")

# Dashboard Metrics Summary Placeholder
st.markdown('### System Architecture Quick Status')
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label='Data Model', value='Star Schema', delta='1 Fact / 4 Dimensions')
with col2:
    st.metric(label='Primary Measure', value='Quantity (Traded Units)')
with col3:
    st.metric(label='Temporal Grain', value= 'Daily Level', delta= '2024 Calendar')

st.markdown('---')
st.caption('Developed as part of Big Data Analytics Frameworks assignment requirements. All rights reserved © 2026.')