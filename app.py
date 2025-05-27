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
    
    # Initialisera dark mode state
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

def apply_custom_css():
    """
    Applicera anpassad CSS baserat på dark/light mode
    
    How to modify:
    - Ändra färger genom att modifiera CSS-variablerna
    - Lägg till fler stilar för olika komponenter
    """
    if st.session_state.dark_mode:
        # Dark mode CSS
        st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #262730;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #262730;
            color: #fafafa;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #3e3e4e;
        }
        .stSelectbox > div > div {
            background-color: #262730;
            color: #fafafa;
        }
        .stTextInput > div > div > input {
            background-color: #262730;
            color: #fafafa;
        }
        .stDataFrame {
            background-color: #1e1e1e;
        }
        div[data-testid="metric-container"] {
            background-color: #262730;
            border: 1px solid #3e3e4e;
            padding: 10px;
            border-radius: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Light mode CSS (default)
        st.markdown("""
        <style>
        .stApp {
            background-color: #ffffff;
            color: #262730;
        }
        div[data-testid="metric-container"] {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 10px;
            border-radius: 5px;
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
        page_title="CPM & Finansiell Analys Platform",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialisera session state
    initialize_global_session_state()
    
    # Applicera custom CSS för dark/light mode
    apply_custom_css()
    
    # Header med dark mode toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📊 CPM & Finansiell Analys Platform")
    with col2:
        # Dark mode toggle
        dark_mode = st.checkbox(
            "🌙 Dark Mode", 
            value=st.session_state.dark_mode,
            help="Växla mellan ljust och mörkt tema"
        )
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.rerun()
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
