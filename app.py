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
    Applicera permanent dark mode CSS för hela applikationen
    
    How to modify:
    - Ändra färger genom att modifiera CSS-variablerna
    - Lägg till fler stilar för olika komponenter
    """
    st.markdown("""
    <style>
    .reportview-container, .sidebar .sidebar-content {
        background-color: #0E1117;
        color: #FFFFFF;
    }
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
        border: 1px solid #3e3e4e;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #3e3e4e;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF6B35 !important;
        color: #ffffff !important;
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
    .stSidebar {
        background-color: #262730;
    }
    .stSidebar .stSelectbox > div > div {
        background-color: #1e1e1e;
        color: #fafafa;
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
