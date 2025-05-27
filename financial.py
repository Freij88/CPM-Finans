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
    if 'total_industry_revenue' not in st.session_state:
        st.session_state.total_industry_revenue = 500  # miljarder USD

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
    Skapa finansiella diagram med Plotly för bättre interaktivitet
    
    How to modify:
    - Ändra diagramtyper från bar/scatter till andra Plotly charts
    - Lägg till fler visualiseringar här
    - Ändra färgskala genom color_discrete_sequence parametern
    """
    if df.empty:
        return None, None, None
    
    # Filtrera ut rader med 0-värden för bättre visualisering
    df_filtered = df[df['Revenue (B USD)'] > 0].copy()
    
    if df_filtered.empty:
        return None, None, None
    
    # Konvertera till Mdr SEK (1 USD ≈ 10.5 SEK ungefär)
    usd_to_sek = 10.5
    df_filtered['Revenue (Mdr SEK)'] = df_filtered['Revenue (B USD)'] * usd_to_sek
    
    # Revenue stapeldiagram
    revenue_chart = px.bar(
        df_filtered,
        x='Company',
        y='Revenue (Mdr SEK)',
        color='Country',
        title='Omsättning per företag (Mdr SEK)',
        hover_data={
            'Revenue (Mdr SEK)': ':.1f',
            'Employees': ':,',
            'Data Source': True
        },
        labels={'Revenue (Mdr SEK)': 'Omsättning (Mdr SEK)'}
    )
    revenue_chart.update_layout(height=400)
    
    # P/E vs Revenue scatter plot
    pe_filtered = df_filtered[df_filtered['P/E Ratio'] > 0].copy()
    pe_chart = None
    
    if not pe_filtered.empty:
        pe_chart = px.scatter(
            pe_filtered,
            x='Revenue (Mdr SEK)',
            y='P/E Ratio',
            size='Employees',
            color='Country',
            hover_name='Company',
            title='P/E-tal vs Omsättning (bubbelstorlek = antal anställda)',
            hover_data={
                'Revenue (Mdr SEK)': ':.1f',
                'P/E Ratio': ':.2f',
                'Employees': ':,',
                'Data Source': True
            },
            labels={
                'Revenue (Mdr SEK)': 'Omsättning (Mdr SEK)',
                'P/E Ratio': 'P/E-tal'
            }
        )
        pe_chart.update_layout(height=400)
    
    # Marknadspenetration diagram
    penetration_chart = px.bar(
        df_filtered,
        x='Company',
        y='Market Penetration (%)',
        color='Country',
        title='Marknadspenetration per företag (%)',
        hover_data={
            'Market Penetration (%)': ':.2f',
            'Revenue (Mdr SEK)': ':.1f',
            'Data Source': True
        },
        labels={'Market Penetration (%)': 'Marknadspenetration (%)'}
    )
    penetration_chart.update_layout(height=400)
    
    return revenue_chart, pe_chart, penetration_chart

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
        
        # Beräkna marknadspenetration med aktuellt värde
        cached_data = calculate_market_penetration(
            st.session_state.financial_data_cache.copy(), 
            st.session_state.total_industry_revenue
        )
        
        # Skapa och visa diagram direkt
        charts = create_financial_charts(cached_data)
        revenue_chart, pe_chart, penetration_chart = charts if charts else (None, None, None)
        
        if revenue_chart:
            col1, col2 = st.columns(2)
            with col1:
                st.caption("💡 Hovra över staplarna för detaljer")
                st.plotly_chart(revenue_chart, use_container_width=True)
            with col2:
                if pe_chart:
                    st.caption("💡 Bubbelstorlek = antal anställda")
                    st.plotly_chart(pe_chart, use_container_width=True)
                else:
                    st.info("💡 P/E-data ej tillgänglig för dessa företag")
        
        # Visa marknadspenetration
        if penetration_chart:
            st.caption("💡 Baserat på total branschomsättning")
            st.plotly_chart(penetration_chart, use_container_width=True)
        
        st.dataframe(cached_data, use_container_width=True)
    
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
        st.subheader("⚙️ Inställningar")
        
        # Branschomsättning input
        total_revenue = st.number_input(
            "Total branschomsättning (miljarder USD)",
            min_value=1.0,
            max_value=10000.0,
            value=float(st.session_state.total_industry_revenue),
            step=10.0,
            help="Total marknadsomsättning för beräkning av marknadspenetration"
        )
        
        if total_revenue != st.session_state.total_industry_revenue:
            st.session_state.total_industry_revenue = total_revenue
            st.success("✅ Branschomsättning uppdaterad!")
            st.rerun()
        
        st.divider()
        
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
                
                # Plotly-diagram med tooltips
                charts = create_financial_charts(financial_df)
                revenue_chart, pe_chart, penetration_chart = charts if charts else (None, None, None)
                
                if revenue_chart:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption("💡 Hovra över staplarna för detaljer")
                        st.altair_chart(revenue_chart, use_container_width=True)
                    with col2:
                        if pe_chart:
                            st.caption("💡 Bubbelstorlek = antal anställda")
                            st.altair_chart(pe_chart, use_container_width=True)
                        else:
                            st.info("💡 P/E-diagram kräver tillgängliga P/E-tal")
                
                # Geografisk heatmap
                st.subheader("🗺️ Geografisk fördelning")
                geo_chart = create_geographic_heatmap(financial_df)
                if geo_chart:
                    st.plotly_chart(geo_chart, use_container_width=True)
                else:
                    st.info("💡 Geografisk data ej tillgänglig")
                
                # Visa tabelldata
                st.subheader("📋 Detaljerad data")
                st.dataframe(financial_df, use_container_width=True)
                
                # Export
                st.subheader("💾 Export")
                csv_data = financial_df.to_csv(index=False)
                st.download_button(
                    label="📁 Ladda ner finansiell data som CSV",
                    data=csv_data,
                    file_name=f"finansiell_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
            else:
                st.error("❌ Kunde inte hämta finansiell data.")
                st.info("💡 Kontrollera ticker-symboler eller prova egen datafil.")
    
    # Hantera uppladdad custom data
    if not custom_df.empty:
        st.subheader("📁 Visualisering av uppladdad data")
        
        # Beräkna marknadspenetration för custom data
        custom_df_processed = calculate_market_penetration(custom_df)
        
        # Skapa enkla visualiseringar för custom data
        if 'Revenue' in custom_df_processed.columns:
            # Konvertera revenue-kolumn för visualisering
            if custom_df_processed['Revenue'].dtype == 'object':
                # Försök konvertera strängar till siffror
                custom_df_processed['Revenue (B USD)'] = pd.to_numeric(
                    custom_df_processed['Revenue'], errors='coerce'
                ) / 1e9
            else:
                custom_df_processed['Revenue (B USD)'] = custom_df_processed['Revenue'] / 1e9
            
            # Skapa stapeldiagram
            fig_custom = px.bar(
                custom_df_processed,
                x='Company',
                y='Revenue (B USD)',
                title='Omsättning per företag (uppladdad data)',
                labels={'Revenue (B USD)': 'Omsättning (miljarder USD)'}
            )
            
            st.plotly_chart(fig_custom, use_container_width=True)
        
        st.dataframe(custom_df_processed, use_container_width=True)
