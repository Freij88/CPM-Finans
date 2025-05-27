"""
Huvudapplikation för CPM-modell, Finansiell Jämförelse och Aktieanalys
Modulär Streamlit-applikation med separata moduler för olika analyser
"""

import streamlit as st
import pandas as pd

# Importera moduler
from cpm import initialize_cpm_session_state, show_cpm_tab
from financial import initialize_financial_session_state, show_financial_tab  
from stocks import initialize_stocks_session_state, show_stocks_tab

# Konfigurera pandas för att undvika warnings
pd.set_option('future.no_silent_downcasting', True)

# Konfiguration av sidan
st.set_page_config(
    page_title="CPM-modell, Finansiell Jämförelse & Aktieanalys",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """
    Initialisera session state för alla moduler
    
    How to modify:
    - Lägg till nya globala variabler här
    - Anropa initialize-funktioner från andra moduler
    """
    # Initialisera varje moduls session state
    initialize_cpm_session_state()
    initialize_financial_session_state() 
    initialize_stocks_session_state()

def main():
    """
    Huvudfunktion för applikationen med tre flikar
    
    How to modify:
    - Lägg till fler flikar genom att utöka tabs-listan
    - Ändra fliknamn här
    - Lägg till ny funktionalitet genom att skapa nya moduler
    """
    initialize_session_state()
    
    st.title("📊 CPM-modell, Finansiell Jämförelse & Aktieanalys")
    st.markdown("### Omfattande analysverktyg för affärsbeslut")
    
    # Skapa tre flikar enligt specifikation
    tab1, tab2, tab3 = st.tabs(["📊 CPM", "💰 Finansiell", "📈 Aktier"])
    
    with tab1:
        # Ladda endast CPM-komponenter
        show_cpm_tab()
    
    with tab2:
        # Ladda endast Financial-komponenter  
        show_financial_tab()
    
    with tab3:
        # Ladda endast Stocks-komponenter
        show_stocks_tab()

if __name__ == "__main__":
    main()