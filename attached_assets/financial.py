"""
Financial analysis module for company financial data comparison.
Handles data fetching, market penetration calculations, and financial visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import altair as alt
from datetime import datetime
from utils import get_country_code, calculate_market_penetration, validate_uploaded_file

def initialize_financial_session_state():
    """
    Initialisera session state för Financial-modulen
    
    How to modify:
    - Lägg till fler förvalda företag i financial_companies
    - Ändra standard ticker-symboler för din bransch
    """
    if 'financial_companies' not in st.session_state:
        st.session_state.financial_companies = ["SAAB-B.ST", "BA.L", "BA"]
    if 'custom_tickers' not in st.session_state:
        st.session_state.custom_tickers = []
    if 'financial_data_cache' not in st.session_state:
        st.session_state.financial_data_cache = pd.DataFrame()

def fetch_financial_data():
    """
    Hämta finansiell data via yfinance för förvalda och anpassade företag
    
    How to change data source:
    - Ersätt yfinance med annan API (t.ex. Alpha Vantage, Quandl)
    - Ändra info.get() anrop för andra datakällor
    - Lägg till API-nyckel hantering här om behövs
    """
    all_tickers = st.session_state.financial_companies + st.session_state.custom_tickers
    financial_data = []
    errors = []
    
    for ticker in all_tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Kontrollera om data faktiskt hämtades
            if not info or len(info) < 5:  # Minimal data check
                errors.append(f"Ingen data hittades för {ticker}")
                continue
            
            # Hämta grundläggande data
            company_name = info.get('longName', info.get('shortName', ticker))
            revenue = info.get('totalRevenue', info.get('revenue', 0))
            employees = info.get('fullTimeEmployees', 0)
            pe_ratio = info.get('trailingPE', info.get('forwardPE', 0))
            country = info.get('country', 'Unknown')
            
            # Konvertera revenue till miljarder för läsbarhet
            revenue_billions = revenue / 1e9 if revenue and revenue > 0 else 0
            
            financial_data.append({
                'Ticker': ticker,
                'Company': company_name,
                'Revenue (B USD)': round(revenue_billions, 2) if revenue_billions > 0 else 0,
                'Employees': employees if employees and employees > 0 else 0,
                'P/E Ratio': round(pe_ratio, 2) if pe_ratio and pe_ratio > 0 else 0,
                'Country': country,
                'CountryCode': get_country_code(country),
                'Data Source': 'Yahoo Finance (yfinance)'
            })
            
        except Exception as e:
            errors.append(f"Fel för {ticker}: {str(e)}")
            continue
    
    # Visa fel om några uppstod
    if errors:
        st.error("⚠️ Följande fel uppstod vid datahämtning:")
        for error in errors:
            st.write(f"• {error}")
        st.info("💡 Prova att ladda upp en egen CSV/Excel-fil som alternativ.")
    
    df = pd.DataFrame(financial_data)
    if not df.empty:
        st.session_state.financial_data_cache = df
    
    return df

def create_financial_charts(df):
    """
    Skapa finansiella diagram med Altair
    
    How to modify:
    - Ändra diagramtyper från bar/circle till andra Altair charts
    - Lägg till fler visualiseringar här
    - Ändra färgskala genom color-parametern
    """
    if df.empty:
        return None, None
    
    # Filtrera ut rader med 0-värden för bättre visualisering
    df_filtered = df[df['Revenue (B USD)'] > 0].copy()
    
    if df_filtered.empty:
        return None, None
    
    # Konvertera till dictionary för Altair
    chart_data = df_filtered.to_dict('records')
    
    # Revenue chart
    revenue_chart = alt.Chart(alt.InlineData(values=chart_data)).mark_bar().encode(
        x=alt.X('Company:N', sort='-y'),
        y=alt.Y('Revenue (B USD):Q', title='Omsättning (miljarder USD)'),
        color=alt.Color('Country:N', title='Land'),
        tooltip=[
            alt.Tooltip('Company:N', title='Företag'),
            alt.Tooltip('Revenue (B USD):Q', title='Omsättning (B USD)', format='.2f'),
            alt.Tooltip('Employees:Q', title='Anställda', format=','),
            alt.Tooltip('Data Source:N', title='Källa')
        ]
    ).properties(
        width=600,
        height=400,
        title='Omsättning per företag (miljarder USD)'
    )
    
    # P/E Ratio chart - bara företag med P/E > 0
    pe_data = [item for item in chart_data if item.get('P/E Ratio', 0) > 0]
    
    if pe_data:
        pe_chart = alt.Chart(alt.InlineData(values=pe_data)).mark_circle(size=100).encode(
            x=alt.X('Revenue (B USD):Q', title='Omsättning (miljarder USD)'),
            y=alt.Y('P/E Ratio:Q', title='P/E-tal'),
            color=alt.Color('Country:N', title='Land'),
            size=alt.Size('Employees:Q', title='Antal anställda', scale=alt.Scale(range=[50, 500])),
            tooltip=[
                alt.Tooltip('Company:N', title='Företag'),
                alt.Tooltip('Revenue (B USD):Q', title='Omsättning (B USD)', format='.2f'),
                alt.Tooltip('P/E Ratio:Q', title='P/E-tal', format='.2f'),
                alt.Tooltip('Employees:Q', title='Anställda', format=','),
                alt.Tooltip('Data Source:N', title='Källa')
            ]
        ).properties(
            width=600,
            height=400,
            title='P/E-tal vs Omsättning (bubbelstorlek = antal anställda)'
        )
    else:
        pe_chart = None
    
    return revenue_chart, pe_chart

def create_geographic_heatmap(df):
    """
    Skapa geografisk heatmap med Plotly
    
    How to modify:
    - Ändra color_continuous_scale för andra färger
    - Lägg till fler hover-data genom hover_data parametern
    - Ändra geografisk projektion i fig.update_layout
    """
    if df.empty:
        return None
    
    # Gruppera data per land och skapa detaljerad hover-information
    country_groups = df.groupby(['Country', 'CountryCode'])
    
    country_data = []
    for (country, country_code), group in country_groups:
        if country_code == 'N/A':
            continue
            
        companies_list = group['Company'].tolist()
        
        country_data.append({
            'Country': country,
            'CountryCode': country_code,
            'Revenue (B USD)': group['Revenue (B USD)'].sum(),
            'Employees': group['Employees'].sum(),
            'Company Count': len(group),
            'Companies': ', '.join(companies_list)
        })
    
    if not country_data:
        return None
        
    country_df = pd.DataFrame(country_data)
    
    # Skapa heatmap med förbättrad hover-information
    fig = px.choropleth(
        country_df,
        locations='CountryCode',
        color='Revenue (B USD)',
        hover_name='Country',
        hover_data={
            'Company Count': True,
            'Revenue (B USD)': ':.2f',
            'Employees': ':,',
            'CountryCode': False,
            'Companies': True
        },
        color_continuous_scale='Viridis',
        title='Geografisk fördelning av omsättning (Source: Yahoo Finance)'
    )
    
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True),
        title_x=0.5
    )
    
    return fig

def show_financial_tab():
    """
    Huvudfunktion för finansiell jämförelse-fliken
    
    How to modify:
    - Lägg till fler parametrar i sidebar
    - Ändra layout genom att modifiera kolumnstrukturen
    - Lägg till automatisk uppdatering genom att ta bort knapp-villkor
    """
    st.header("💰 Finansiell Jämförelse")
    
    # Visa direkt stapeldiagram om det finns cached data
    if not st.session_state.financial_data_cache.empty:
        st.subheader("📊 Senaste finansiella data")
        st.caption("🔗 Datakälla: Yahoo Finance (yfinance)")
        
        # Skapa och visa diagram direkt
        revenue_chart, pe_chart = create_financial_charts(st.session_state.financial_data_cache)
        
        if revenue_chart:
            col1, col2 = st.columns(2)
            with col1:
                st.caption("💡 Hovra över staplarna för detaljer")
                st.altair_chart(revenue_chart, use_container_width=True)
            with col2:
                if pe_chart:
                    st.caption("💡 Bubbelstorlek = antal anställda")
                    st.altair_chart(pe_chart, use_container_width=True)
        
        st.dataframe(st.session_state.financial_data_cache, use_container_width=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Företagshantering")
        
        # Visa förvalda företag med borttagning
        st.write("**Förvalda företag:**")
        companies_to_remove = []
        for ticker in st.session_state.financial_companies:
            col_ticker, col_remove = st.columns([3, 1])
            with col_ticker:
                st.write(f"• {ticker}")
            with col_remove:
                if st.button("🗑️", key=f"remove_default_{ticker}", help=f"Ta bort {ticker}"):
                    companies_to_remove.append(ticker)
        
        # Ta bort markerade företag
        for ticker in companies_to_remove:
            st.session_state.financial_companies.remove(ticker)
            st.success(f"Tog bort {ticker}")
            st.rerun()
        
        # Lägg till anpassade ticker-symboler
        st.write("**Lägg till fler företag:**")
        new_ticker = st.text_input("Ticker-symbol (t.ex. AAPL, MSFT):")
        
        if st.button("➕ Lägg till") and new_ticker:
            ticker_upper = new_ticker.upper()
            if ticker_upper not in st.session_state.custom_tickers and ticker_upper not in st.session_state.financial_companies:
                st.session_state.custom_tickers.append(ticker_upper)
                st.success(f"Lade till {ticker_upper}")
                st.rerun()
        
        # Visa tillagda företag med borttagning
        if st.session_state.custom_tickers:
            st.write("**Tillagda företag:**")
            custom_to_remove = []
            for ticker in st.session_state.custom_tickers:
                col_ticker, col_remove = st.columns([3, 1])
                with col_ticker:
                    st.write(f"• {ticker}")
                with col_remove:
                    if st.button("🗑️", key=f"remove_custom_{ticker}", help=f"Ta bort {ticker}"):
                        custom_to_remove.append(ticker)
            
            # Ta bort markerade anpassade företag
            for ticker in custom_to_remove:
                st.session_state.custom_tickers.remove(ticker)
                st.success(f"Tog bort {ticker}")
                st.rerun()
    
    with col2:
        st.subheader("📁 Alternativ datakälla")
        st.info("Ladda upp CSV/Excel med kolumner: Company, Revenue, Employees, CountryCode")
        
        required_columns = ['Company', 'Revenue', 'Employees', 'CountryCode']
        uploaded_file = st.file_uploader(
            "Välj fil", 
            type=['csv', 'xlsx', 'xls'],
            help="Filen ska innehålla kolumnerna: Company, Revenue, Employees, CountryCode"
        )
        
        custom_df = validate_uploaded_file(uploaded_file, required_columns)
        
        if not custom_df.empty:
            st.success("✅ Fil laddad framgångsrikt!")
            st.dataframe(custom_df.head(), use_container_width=True)
    
    # Marknadspenetration förklaring
    st.info("**💡 Marknadspenetration:** Företagets omsättning ÷ total branschomsättning (500B USD referens)")
    
    # Hämta finansiell data
    if st.button("🔄 Hämta finansiell data från Yahoo Finance", type="primary"):
        with st.spinner("Hämtar data från Yahoo Finance..."):
            financial_df = fetch_financial_data()
            
            if not financial_df.empty:
                # Beräkna marknadspenetration
                financial_df = calculate_market_penetration(financial_df)
                
                st.success(f"✅ Hämtade data för {len(financial_df)} företag!")
                
                # Skapa diagram
                st.subheader("📈 Visualiseringar")
                
                # Altair-diagram med tooltips
                revenue_chart, pe_chart = create_financial_charts(financial_df)
                
                if revenue_chart and pe_chart:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption("💡 Hovra över staplarna för detaljer (källa: Yahoo Finance)")
                        st.altair_chart(revenue_chart, use_container_width=True)
                    with col2:
                        st.caption("💡 Bubbelstorlek = antal anställda (källa: Yahoo Finance)")
                        st.altair_chart(pe_chart, use_container_width=True)
                
                # Geografisk heatmap
                geo_heatmap = create_geographic_heatmap(financial_df)
                if geo_heatmap:
                    st.subheader("🌍 Geografisk fördelning")
                    st.caption("💡 Hovra över länder för att se alla företag")
                    st.plotly_chart(geo_heatmap, use_container_width=True)
                
                # Export-funktion
                st.subheader("💾 Export")
                csv_financial = financial_df.to_csv(index=False, sep=';')
                st.download_button(
                    label="📁 Ladda ner finansiell data som CSV",
                    data=csv_financial,
                    file_name=f"finansiell_jamforelse_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.error("❌ Kunde inte hämta finansiell data. Försök med fallback-uppladdning.")
    
    # Visa anpassad data om den laddats upp
    if not custom_df.empty:
        st.subheader("📁 Uppladdad anpassad data")
        st.caption("🔗 Datakälla: Användarladdad fil")
        st.dataframe(custom_df, use_container_width=True)
        
        # Skapa enkla visualiseringar för anpassad data
        if 'Revenue' in custom_df.columns and 'Company' in custom_df.columns:
            custom_data = custom_df.to_dict('records')
            custom_chart = alt.Chart(alt.InlineData(values=custom_data)).mark_bar().encode(
                x=alt.X('Company:N', sort='-y'),
                y=alt.Y('Revenue:Q'),
                tooltip=['Company:N', 'Revenue:Q', 'Employees:Q'] if 'Employees' in custom_df.columns else ['Company:N', 'Revenue:Q']
            ).properties(
                width=600,
                height=300,
                title='Anpassad data - Intäkter per företag'
            )
            st.altair_chart(custom_chart, use_container_width=True)