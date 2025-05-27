"""
Huvudapplikation för CPM & Finansiell Analys Platform
En omfattande Streamlit-baserad affärsanalysplattform med CPM-modellering, 
finansiell jämförelse och aktieanalys med live-data från Yahoo Finance.
"""

import streamlit as st
import pandas as pd
from cpm import initialize_cpm_session_state, show_cpm_tab
from financial import initialize_financial_session_state, show_financial_tab
from stocks import initialize_stocks_session_state, show_stocks_tab

def initialize_global_session_state():
    """
    Initialisera global session state för hela applikationen
    
    How to modify:
    - Lägg till globala inställningar här
    - Ändra standard-flik genom att ändra default_tab
    """
    if 'app_initialized' not in st.session_state:
        st.session_state.app_initialized = True
        # Initialisera alla moduler
        initialize_cpm_session_state()
        initialize_financial_session_state()
        initialize_stocks_session_state()

def apply_dark_mode_css():
    """
    Applicera snyggt dark mode CSS med bra kontrast och läsbarhet
    
    How to modify:
    - Ändra färger genom att modifiera CSS-variablerna
    - Lägg till fler stilar för olika komponenter
    """
    st.markdown("""
    <style>
    /* Huvudbakgrund */
    .stApp {
        background-color: #0f0f0f;
        color: #ffffff;
    }
    
    /* Sidebar styling */
    .stSidebar {
        background-color: #1a1a1a !important;
    }
    .stSidebar .stMarkdown {
        color: #ffffff !important;
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: #ffffff !important;
    }
    .stSidebar .stSelectbox label {
        color: #ffffff !important;
    }
    .stSidebar .stTextInput label {
        color: #ffffff !important;
    }
    .stSidebar .stButton button {
        background-color: #333333;
        color: #ffffff;
        border: 1px solid #555555;
    }
    
    /* Flikar */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a1a;
        padding: 5px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #333333;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 5px;
        margin: 2px;
        font-weight: 500;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #444444;
        color: #ffffff;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff6b35 !important;
        color: #ffffff !important;
        border-color: #ff6b35 !important;
    }
    
    /* Input fält */
    .stSelectbox > div > div {
        background-color: #333333 !important;
        color: #ffffff !important;
        border: 1px solid #555555 !important;
    }
    .stTextInput > div > div > input {
        background-color: #333333 !important;
        color: #ffffff !important;
        border: 1px solid #555555 !important;
    }
    .stNumberInput > div > div > input {
        background-color: #333333 !important;
        color: #ffffff !important;
        border: 1px solid #555555 !important;
    }
    
    /* Knappar */
    .stButton button {
        background-color: #ff6b35;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        font-weight: 500;
    }
    .stButton button:hover {
        background-color: #e55a2b;
        color: #ffffff;
    }
    
    /* Dataframe och tabeller */
    .stDataFrame {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 5px;
    }
    .stDataFrame table {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    .stDataFrame thead tr th {
        background-color: #333333 !important;
        color: #ffffff !important;
        border-bottom: 1px solid #555555;
    }
    .stDataFrame tbody tr td {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border-bottom: 1px solid #2a2a2a;
    }
    
    /* Metrics containers */
    div[data-testid="metric-container"] {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        padding: 15px;
        border-radius: 8px;
        color: #ffffff;
    }
    div[data-testid="metric-container"] label {
        color: #cccccc !important;
    }
    div[data-testid="metric-container"] div {
        color: #ffffff !important;
    }
    
    /* Sliders */
    .stSlider > div > div > div > div {
        background-color: #ff6b35;
    }
    .stSlider label {
        color: #ffffff !important;
    }
    
    /* Info, success, error boxes */
    .stInfo {
        background-color: #1a3d5c;
        border: 1px solid #2c5aa0;
        color: #ffffff;
    }
    .stSuccess {
        background-color: #1a4d3a;
        border: 1px solid #2d8a5a;
        color: #ffffff;
    }
    .stError {
        background-color: #5c1a1a;
        border: 1px solid #a02c2c;
        color: #ffffff;
    }
    
    /* Checkboxes */
    .stCheckbox label {
        color: #ffffff !important;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        background-color: #333333 !important;
        color: #ffffff !important;
        border: 1px solid #555555 !important;
    }
    
    /* File uploader */
    .stFileUploader label {
        color: #ffffff !important;
    }
    .stFileUploader > div > div {
        background-color: #333333;
        border: 1px solid #555555;
        color: #ffffff;
    }
    
    /* Plotly chart background fix */
    .js-plotly-plot {
        background-color: #1a1a1a !important;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """
    Huvudfunktion som koordinerar hela applikationen
    
    How to modify:
    - Lägg till fler flikar genom att utöka tabs-listan
    - Ändra sidkonfiguration genom page_config parametrar
    - Lägg till globala inställningar i sidebar
    """
    # Konfigurera sidan
    st.set_page_config(
        page_title="CPM + Finansiell + Aktier",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="auto"
    )
    
    # Initialisera session state
    initialize_global_session_state()
    
    # Applicera permanent dark mode CSS
    apply_dark_mode_css()
    
    # Header
    st.title("📊 CPM & Finansiell Analys Platform")
    st.markdown("""
    ### Omfattande affärsanalysverktyg för strategisk beslutsfattning
    
    **Denna plattform erbjuder:**
    - 🎯 **CPM-analys**: Critical Path Method med dynamiska CSF:er och ROC-viktning
    - 💰 **Finansiell jämförelse**: Live företagsdata med geografisk visualisering  
    - 📈 **Aktieanalys**: Realtids aktiedata och teknisk analys
    
    ---
    """)
    
    # Skapa flikar för de tre huvudmodulerna
    tabs = st.tabs(["📊 CPM-analys", "💰 Finansiell jämförelse", "📈 Aktieanalys"])
    
    # CPM-analys flik
    with tabs[0]:
        try:
            show_cpm_tab()
        except Exception as e:
            st.error(f"❌ Fel i CPM-modulen: {str(e)}")
            st.info("💡 Kontakta support om problemet kvarstår.")
    
    # Finansiell jämförelse flik  
    with tabs[1]:
        try:
            show_financial_tab()
        except Exception as e:
            st.error(f"❌ Fel i finansiell modul: {str(e)}")
            st.info("💡 Prova att ladda upp egen data som alternativ.")
    
    # Aktieanalys flik
    with tabs[2]:
        try:
            show_stocks_tab()
        except Exception as e:
            st.error(f"❌ Fel i aktie-modulen: {str(e)}")
            st.info("💡 Kontrollera internet-anslutning och ticker-symboler.")
    
    # Global sidebar med applikationsinformation
    with st.sidebar:
        st.markdown("---")
        st.subheader("ℹ️ Om plattformen")
        
        st.markdown("""
        **Utvecklad för:**
        - Strategisk affärsanalys
        - Leverantörsjämförelser  
        - Investeringsbeslut
        - Marknadsanalys
        
        **Datakällor:**
        - Yahoo Finance API (finansiell & aktiedata)
        - Användarladdade filer (CSV/Excel)
        - Manuell inmatning
        """)
        
        st.markdown("---")
        st.caption("Version 1.0 | Powered by Streamlit")
        
        # Visa applikationsstatus
        if st.session_state.get('app_initialized'):
            st.success("✅ Applikation initialiserad")
        
        # Global reset-knapp (för utveckling/debugging)
        if st.button("🔄 Återställ all data", help="Rensa all session data"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Data återställd!")
            st.rerun()

if __name__ == "__main__":
    main()
