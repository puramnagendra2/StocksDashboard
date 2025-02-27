import streamlit as st
import streamlit_lottie as stl
import plotly.express as px
import streamlit_option_menu as som

import requests_cache
import random

# Data Libraries
from datetime import datetime
import numpy as np
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf


# Rate Limits
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter
class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
   pass

session = CachedLimiterSession(
   limiter=Limiter(RequestRate(2, Duration.SECOND*5)),  # max 2 requests per 5 seconds
   bucket_class=MemoryQueueBucket,
   backend=SQLiteCache("yfinance.cache"),
)


# Defined Functions
def format_to_crores(number):
    crore_value = number / 10**7  # 1 crore = 10 million (10^7)
    return f"{crore_value:,.2f} Cr"

# Setting Page Configurations
st.set_page_config(page_title="Stock Dashboard", page_icon=":clipboard:", layout="wide")

alt.theme.enable("dark")

# Loading CSV Dataset
df = pd.read_csv("./Misc Files/filtered_nifty_50.csv")

# Options for choosing
with st.form("input-form", border=False):
    col1, col2, col3 = st.columns([1, 0.5, 1])
    with col1:
        stocks = df["NAME OF COMPANY"].to_list()
        stock_name = st.selectbox(label="Select Stock Symbol", options=stocks, label_visibility="collapsed")
    with col2:
        durations = {"5D":"5d", "1M": "1mo", "3M":"3mo", "6M": "6mo", "1Y":"1y", "2Y":"2y", "5Y":"5y", "10Y":"10y", "YTD":"ytd", "MAX":"max"}
        time_frame = st.selectbox(label="Time Frame", options=durations.keys(), label_visibility="collapsed")
    with col3:
        create = st.form_submit_button("Create Dashboard", type="primary")

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.0 Safari/537.36',
]

session = requests_cache.CachedSession('yfinance.cache')
session.headers['User-Agent'] = random.choice(user_agents)

if create:
    symbol = df.loc[df["NAME OF COMPANY"] == stock_name, 'SYMBOL'].values[0] + ".NS"
    data = yf.Ticker(symbol, session=session)

    # st.write(data.actions)
    
    # Store data in session state
    st.session_state["stock_data"] = data
    st.session_state["stock_name"] = stock_name
    st.session_state["symbol"] = symbol

# Ensure data persists after reload
if "stock_data" in st.session_state:
    data = st.session_state["stock_data"]
    stock_name = st.session_state["stock_name"]
    symbol = st.session_state["symbol"]

    c_name, curr = st.columns([1.5, 1])

    with c_name:
        # Display stock details
        st.header(f"{stock_name} ({symbol})")
    
    with curr:
        st.header(f" Current Price Rs. {data.info.get('currentPrice', 'No Data')} ")
        # st.write(data.info.keys())
    st.link_button(label="Website Link", url=data.info.get('website', 'No Data'), type="primary")
    st.divider()
    # Navigation

    menu_items = ["Overview", "Charts", "Financials", "Fundamentals", "Projections"]
    navigation_menu = som.option_menu(
        menu_title=None,
        menu_icon=None,
        options= menu_items,
        icons=["journal", "bar-chart", "bank", "card-checklist", "graph-up-arrow"],
        orientation="horizontal"
    )

    # Overview Section
    if navigation_menu == "Overview":
        st.subheader(":blue[Summary]")
        with st.expander(f" {stock_name}"):
            st.text(data.info.get('longBusinessSummary', 'No Data'))
        
        officers, mar_cap, emp_count = st.columns([2, 1, 1], gap="small")
        
        # Officers
        # st.write(data.info.get('companyOfficers'))
        with officers:
            st.subheader(":blue[Officers]")
            off1, off2 = st.columns([1, 1], gap="small")
            officers = data.info.get('companyOfficers', 'No Data')
            with off1:
                with st.popover(label=officers[0]['title'], icon=":material/badge:"):
                    st.metric(label=officers[0]['title'], value=officers[0]['name'])

            with off2:
                with st.popover(label=officers[1]['title'], icon=":material/badge:"):
                    st.metric(label=officers[1]['title'], value=officers[1]['name'])

        # Market Capital
        with mar_cap:
            st.subheader(":blue[Market Capital]")
            market_cap, empty = st.columns([2, 1], gap="small")
            with market_cap:
                st.metric(label="Market Cap", value=format_to_crores(data.info.get('marketCap', 'No Data')), label_visibility="collapsed")
        
        # Employee Count
        with emp_count:
            st.subheader(":blue[Employee Count]")
            market_cap, empty = st.columns(2, gap="small")
            with market_cap:
                st.metric(label="Market Cap", value=data.info.get('fullTimeEmployees', 'No Data'), label_visibility="collapsed")

        # Location
        st.subheader(":blue[Location]")
        addr, city, country = st.columns(3, gap="small")
        with addr:
            st.metric(label="Address", value=data.info.get('address1', 'No Data'))
        with city:
            st.metric(label="City", value=data.info.get('city', 'No Data'))
        with country:
            st.metric(label="Country", value=data.info.get('country', 'No Data'))
        
        # Sector and Industry

        st.subheader(":blue[Sector & Industry]")
        emp1, sector, industry, emp2 = st.columns([0.5, 2, 2, 0.5], gap="medium")
        with sector:
            st.metric(label="Sector", value=data.info.get('sector', 'No Data'), border=True)
        with industry:
            st.metric(label="Industry", value=data.info.get('industry', 'No Data'), border=True)
        
        st.divider()
        
        # News
        st.subheader(":blue[News]")

        news = data.news
        length_of_news = len(data.news)
        # st.write(data.news[0])
        for i in range(length_of_news):
            news_articles = news[i]['content']
            with st.expander(news_articles['title']):
                st.write(news_articles['summary'])
                provider, provider_site, link = st.tabs(tabs=['News Provider', 'Webiste', 'Reference Link'])

                with provider:
                    st.subheader(news_articles['provider']['displayName'])
                with provider_site:
                    st.link_button(label="Provider Site", url=news_articles['provider']['url'], type="secondary")
                with link: 
                    st.link_button(label="Reference", url=news_articles['thumbnail']['originalUrl'] if news_articles['thumbnail'] else "No Data", type="primary")

    elif navigation_menu == "Charts":
        frame, space = st.columns([3, 0.5])
        with st.container(border=True):
            with frame:
                time_frames = som.option_menu(
                    menu_title=None,
                    options=list(durations.keys()),
                    icons=None,
                    orientation="horizontal"
                )

                st.session_state['time_frames'] = time_frames
            time_data = data.history(period=durations[time_frames]).reset_index()
            #st.write(time_data['Close'])
            #st.write(time_data.columns)


            line_chart, candlestick = st.tabs(['Line Chart', 'Candlestick'])

            # Line Chart
            with line_chart:
                # st.subheader(f"Line Chart for {time_frames}")
                line_chart = px.line(data_frame=time_data, x="Date", y="Close")
                st.plotly_chart(line_chart, theme="streamlit")
            
            # Candlestick Chart
            with candlestick:
                # st.subheader(f"Candlestick Chart for {time_frames}")
                candlestick_chart = go.Figure(data=[go.Candlestick(x=time_data['Date'],
                        open=time_data['Open'],
                        high=time_data['High'],
                        low=time_data['Low'],
                        close=time_data['Close'],
                        increasing_line_color= 'cyan', decreasing_line_color= 'gray')])
                candlestick_chart.update_layout(xaxis_rangeslider_visible=False)
                st.plotly_chart(candlestick_chart, theme="streamlit")
        
    elif navigation_menu == "Financials":
        st.header(":red[Quarterly Analysis]")

        st.subheader(":blue[Quarterly Balance Sheet]")
        st.write(data.quarterly_balancesheet)

        st.subheader(":blue[Quarterly Income Statement]")
        st.write(data.quarterly_incomestmt)

        st.divider()
        st.header(":red[Annual Analysis]")

        st.subheader(":blue[Balance Sheet]")
        balanceSheet = data.balancesheet

        # Dates Processing
        dates = list(balanceSheet.columns)
        formatted_dates = [str(i.year) for i in dates]

        # Rows Processing
        transposed_balanceSheet = balanceSheet.T
        transposed_balanceSheet['Year'] = formatted_dates
        transposed_balanceSheet = transposed_balanceSheet.head(4)

        # Printing
        # st.write(transposed_balanceSheet)

        # Balance Sheet Charts
        shares_number, debt_chart = st.columns(2, gap="large")
        with shares_number:
            bar_chart = px.bar(data_frame=transposed_balanceSheet, x="Year", y="Ordinary Shares Number", color="Year")
            bar_chart.update_layout(title="Number of Ordinary Shares")
            st.plotly_chart(bar_chart, theme="streamlit")

        with debt_chart:
            present_debt = None
            if 'Net Debt' in transposed_balanceSheet.columns:
                present_debt = 'Net Debt'
            else:
                present_debt = 'Current Debt'
            debt_bar = go.Figure(data=[
                    go.Bar(name="Total Debt", x=transposed_balanceSheet['Year'], y=transposed_balanceSheet['Total Debt'], marker_color='rgb(55, 83, 109)'),
                    go.Bar(name="Net Debt", x=transposed_balanceSheet['Year'], y=transposed_balanceSheet[present_debt],
                            marker_color='rgb(26, 118, 255)')
                ], layout=dict(barcornerradius=10,)
            )

            debt_bar.update_layout(
                title={
                    'text': 'Total Debt vs Net Debt',
                    'x': 0.5,  # Center the title horizontally
                    'xanchor': 'center'
                },
                xaxis_title='Year',  
                yaxis_title='Debt'
            )

            st.plotly_chart(debt_bar, theme="streamlit")

        # Income Statement
        st.subheader(":blue[Income Statement]")
        incomeStmt = data.incomestmt

        # Dates Processing
        dates = list(incomeStmt.columns)
        formatted_dates = [str(i.year) for i in dates]

        transposed_incomeStmt = incomeStmt.T
        transposed_incomeStmt['Year'] = formatted_dates
        transposed_incomeStmt = transposed_incomeStmt.head(4)

        # Printing
        # st.write(transposed_incomeStmt)        

        # EPS Bar Chart
        eps_bar = go.Figure(data=[
                go.Bar(name="Diluted EPS", x=transposed_incomeStmt['Year'], y=transposed_incomeStmt['Diluted EPS'], marker_color='rgb(70, 237, 200)'),
                go.Bar(name="Basic EPS", x=transposed_incomeStmt['Year'], y=transposed_incomeStmt['Basic EPS'], marker_color='rgb(55, 77, 124)'),
            ], layout=dict(barcornerradius=10,)
        )
        eps_bar.update_layout(
            title={
                'text': 'Yearly Basic EPS',
                'x': 0.5,  # Center the title horizontally
                'xanchor': 'center'
            },
            xaxis_title='Year',  
            yaxis_title='EPS Value',
            height=500
        )
        st.plotly_chart(eps_bar, theme="streamlit")        
    

        # Operating Revenue vs Operating Income
        ebitda_bar = go.Figure(data=[
                go.Bar(name="Total Revenue", x=transposed_incomeStmt['Year'], y=transposed_incomeStmt['Total Revenue'], marker_color='rgb(55, 77, 124)'),
                go.Bar(name="Net Income", x=transposed_incomeStmt['Year'], y=transposed_incomeStmt['Net Income'], marker_color='rgb(70, 237, 200)'),
            ], layout=dict(barcornerradius=10,)
        )

        ebitda_bar.update_layout(
            title={
                'text': 'Total Revenue vs Net Income',
                'x': 0.5,  # Center the title horizontally
                'xanchor': 'center'
            },
            xaxis_title='Year',  
            yaxis_title='Value',
            height=500
        )
        st.plotly_chart(ebitda_bar, theme="streamlit")

    elif navigation_menu == "Fundamentals":
        st.header("Fundamentals")
    else:
        st.header("Projections")
            
