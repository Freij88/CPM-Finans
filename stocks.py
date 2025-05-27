"""
Stock analysis module for real-time stock data visualization.
Handles stock data fetching, period analysis, and interactive charts.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
from utils import validate_uploaded_file

def initialize_stocks_session_state():
    """
    Initialisera session state för Stocks-modulen
    
    How to modify:
    - Lägg till fler standard tickers i default_tickers
    - Ändra standardperiod från "30 dagar"
    """
    if 'selected_tickers' not in st.session_state:
        st.session_state.selected_tickers = []
    if 'stock_period' not in st.session_state:
        st.session_state.stock_period = "30 dagar"

def get_period_mapping():
    """
    Mappning från svenska perioder till yfinance-format
    
    How to modify:
    - Lägg till fler perioder i mappningen
    - Ändra svenska namn för perioderna
    """
    return {
        "1 dag": "1d",
        "7 dagar": "7d", 
        "30 dagar": "1mo",
        "90 dagar": "3mo",
        "1 år": "1y",
        "5 år": "5y"
    }

def fetch_stock_data(ticker, period):
    """
    Hämta aktiedata för en given ticker och period
    
    Args:
        ticker: Aktiesymbol (t.ex. "AAPL")
        period: Period i yfinance-format (t.ex. "1mo")
    
    Returns:
        DataFrame med aktiedata eller None vid fel
        
    How to change data source:
    - Ersätt yf.download() med annan datakälla API
    - Lägg till API-nyckel hantering här om behövs
    - Ändra kolumnnamn för andra datakällor
    """
    try:
        # Hämta data från Yahoo Finance
        stock_data = yf.download(ticker, period=period, progress=False)
        
        if stock_data.empty:
            return None
            
        # Lägg till ticker-kolumn och reset index
        stock_data = stock_data.reset_index()
        stock_data['Ticker'] = ticker
        
        # Standardisera kolumnnamn
        if 'Adj Close' in stock_data.columns:
            stock_data['Price'] = stock_data['Adj Close']
        elif 'Close' in stock_data.columns:
            stock_data['Price'] = stock_data['Close']
        else:
            return None
            
        return stock_data
        
    except Exception as e:
        st.error(f"Fel vid hämtning av {ticker}: {str(e)}")
        return None

def calculate_stock_metrics(df):
    """
    Beräkna nyckeltal för aktiedata
    
    How to modify:
    - Lägg till fler metriker (volatilitet, Sharpe ratio, etc.)
    - Ändra beräkningsmetoder för procent-förändring
    """
    if df is None or df.empty:
        return None
        
    current_price = df['Price'].iloc[-1]
    start_price = df['Price'].iloc[0]
    highest_price = df['Price'].max()
    lowest_price = df['Price'].min()
    
    percent_change = ((current_price - start_price) / start_price) * 100
    
    return {
        'current_price': current_price,
        'percent_change': percent_change,
        'highest_price': highest_price,
        'lowest_price': lowest_price
    }

def plot_stock_chart(combined_df):
    """
    Skapa interaktivt linjediagram för aktiedata
    
    How to modify:
    - Ändra färger genom att modifiera line parametern
    - Lägg till tekniska indikatorer (moving averages, etc.)
    - Ändra diagramtyp från line till candlestick
    """
    if combined_df is None or combined_df.empty:
        return None
        
    fig = go.Figure()
    
    # Lägg till en linje för varje ticker
    for ticker in combined_df['Ticker'].unique():
        ticker_data = combined_df[combined_df['Ticker'] == ticker]
        
        fig.add_trace(go.Scatter(
            x=ticker_data['Date'],
            y=ticker_data['Price'],
            mode='lines',
            name=ticker,
            line=dict(width=2),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Datum: %{x}<br>' +
                         'Pris: $%{y:.2f}<br>' +
                         'Källa: Yahoo Finance<extra></extra>'
        ))
    
    fig.update_layout(
        title='Aktiepriser över tid (Källa: Yahoo Finance)',
        xaxis_title='Datum',
        yaxis_title='Pris (USD)',
        hovermode='x unified',
        showlegend=True,
        height=500,
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
        font=dict(color='white'),
        xaxis=dict(gridcolor='#333333', color='white'),
        yaxis=dict(gridcolor='#333333', color='white'),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
    )
    
    return fig

def show_stocks_tab():
    """
    Huvudfunktion för aktie-analys-fliken
    
    How to modify:
    - Lägg till fler input-metoder (multiselect, file upload)
    - Ändra layout genom att modifiera kolumnstrukturen
    - Lägg till teknisk analys sektion
    """
    st.header("📈 Aktieanalys")
    st.markdown("### Realtids aktiedata och prisanalys")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Välj aktier att analysera")
        
        # Input för ticker-symboler
        ticker_input = st.text_input(
            "Ange ticker-symboler (separera med komma):",
            placeholder="t.ex. AAPL, MSFT, GOOGL",
            help="Ange aktiesymboler för de företag du vill analysera"
        )
        
        # Alternativ: multiselect för populära aktier
        popular_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "SAAB-B.ST", "VOLV-B.ST"]
        selected_popular = st.multiselect(
            "Eller välj från populära aktier:",
            popular_stocks,
            help="Välj från en lista med populära aktier"
        )
        
        # Kombinera inputs
        all_tickers = []
        if ticker_input:
            all_tickers.extend([t.strip().upper() for t in ticker_input.split(',') if t.strip()])
        if selected_popular:
            all_tickers.extend(selected_popular)
        
        # Ta bort dubbletter
        all_tickers = list(set(all_tickers))
        
        if all_tickers:
            st.session_state.selected_tickers = all_tickers
            st.success(f"Valda aktier: {', '.join(all_tickers)}")
    
    with col2:
        st.subheader("📅 Tidsperiod")
        
        period_options = list(get_period_mapping().keys())
        selected_period = st.selectbox(
            "Välj analysperiod:",
            period_options,
            index=period_options.index(st.session_state.stock_period),
            help="Välj hur långt tillbaka i tiden du vill analysera"
        )
        st.session_state.stock_period = selected_period
        
        # Fallback file upload
        st.subheader("📁 Alternativ datakälla")
        st.info("Om aktiedata inte kan hämtas, ladda upp CSV med kolumner: Date, Ticker, Price")
        
        uploaded_file = st.file_uploader(
            "Ladda upp aktiedata (CSV)",
            type=['csv'],
            help="CSV-fil med kolumner: Date, Ticker, Price"
        )
    
    # Hämta och visa aktiedata
    if st.session_state.selected_tickers:
        if st.button("📊 Hämta aktiedata", type="primary"):
            yf_period = get_period_mapping()[selected_period]
            
            with st.spinner(f"Hämtar aktiedata för {len(st.session_state.selected_tickers)} aktier..."):
                combined_data = []
                successful_tickers = []
                failed_tickers = []
                
                for ticker in st.session_state.selected_tickers:
                    stock_df = fetch_stock_data(ticker, yf_period)
                    if stock_df is not None:
                        combined_data.append(stock_df)
                        successful_tickers.append(ticker)
                    else:
                        failed_tickers.append(ticker)
                
                if combined_data:
                    # Kombinera all data
                    combined_df = pd.concat(combined_data, ignore_index=True)
                    
                    st.success(f"✅ Hämtade data för {len(successful_tickers)} aktier!")
                    
                    if failed_tickers:
                        st.warning(f"⚠️ Kunde inte hämta data för: {', '.join(failed_tickers)}")
                    
                    # Visa nyckeltal
                    st.subheader("📊 Nyckeltal")
                    
                    metrics_cols = st.columns(len(successful_tickers))
                    
                    for i, ticker in enumerate(successful_tickers):
                        ticker_data = combined_df[combined_df['Ticker'] == ticker]
                        metrics = calculate_stock_metrics(ticker_data)
                        
                        if metrics:
                            with metrics_cols[i]:
                                st.metric(
                                    label=f"{ticker}",
                                    value=f"${metrics['current_price']:.2f}",
                                    delta=f"{metrics['percent_change']:.2f}%"
                                )
                                st.caption(f"Max: ${metrics['highest_price']:.2f}")
                                st.caption(f"Min: ${metrics['lowest_price']:.2f}")
                    
                    # Visa diagram
                    st.subheader("📈 Prisdiagram")
                    chart = plot_stock_chart(combined_df)
                    if chart:
                        st.plotly_chart(chart, use_container_width=True)
                    
                    # Visa rådata
                    st.subheader("📋 Rådata")
                    st.caption("🔗 Datakälla: Yahoo Finance (yfinance)")
                    st.dataframe(combined_df, use_container_width=True)
                    
                    # Export
                    st.subheader("💾 Export")
                    csv_data = combined_df.to_csv(index=False)
                    st.download_button(
                        label="📁 Ladda ner aktiedata som CSV",
                        data=csv_data,
                        file_name=f"aktiedata_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
                    
                else:
                    st.error("❌ Kunde inte hämta aktiedata för någon av de valda symbolerna.")
                    st.info("💡 Prova att ladda upp egen CSV-fil som alternativ.")
    
    # Hantera uppladdat data
    if uploaded_file is not None:
        required_columns = ['Date', 'Ticker', 'Price']
        uploaded_df = validate_uploaded_file(uploaded_file, required_columns)
        
        if not uploaded_df.empty:
            st.subheader("📁 Uppladdad aktiedata")
            st.caption("🔗 Datakälla: Användarladdad fil")
            
            # Konvertera Date-kolumn
            try:
                uploaded_df['Date'] = pd.to_datetime(uploaded_df['Date'])
                
                # Visa diagram för uppladdad data
                chart = plot_stock_chart(uploaded_df)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
                
                st.dataframe(uploaded_df, use_container_width=True)
                
            except Exception as e:
                st.error(f"Fel vid bearbetning av uppladdad data: {str(e)}")
        else:
            st.error("❌ Filen måste innehålla kolumnerna: Date, Ticker, Price")
    
    # Hjälpsektion
    with st.expander("💡 Hjälp och tips"):
        st.markdown("""
        **Så använder du aktieanalys-fliken:**
        
        1. **Lägg till aktier:** Skriv ticker-symboler (t.ex. AAPL, MSFT) eller välj från listan
        2. **Välj period:** Bestäm hur långt tillbaka du vill analysera
        3. **Hämta data:** Klicka på knappen för att ladda data från Yahoo Finance
        4. **Analysera:** Titta på nyckeltal, diagram och rådata
        
        **Tips för ticker-symboler:**
        - Amerikanska aktier: AAPL, MSFT, GOOGL
        - Svenska aktier: SAAB-B.ST, VOLV-B.ST (lägg till .ST)
        - Europeiska aktier: SAP.DE, ASML.AS
        
        **Om data inte kan hämtas:**
        - Kontrollera att ticker-symbolen är korrekt
        - Prova en kortare tidsperiod
        - Ladda upp egen CSV-fil som alternativ
        """)
