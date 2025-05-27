"""
CPM (Critical Path Method) analysis module for ILS software comparison.
Handles CSF management, ROC weighting, and vendor evaluation.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils import calculate_roc_weights, export_to_csv

def initialize_cpm_session_state():
    """
    Initialisera session state för CPM-modulen
    
    How to modify:
    - Lägg till fler CSF:er i csf_list
    - Ändra standardleverantörer i vendor_list
    - Justera default-betyg från 1 till annat värde
    """
    if 'csf_list' not in st.session_state:
        st.session_state.csf_list = [
            "Efterlevnad av ILS-ramverk",
            "Pris för kund",
            "Tidsbesparing",
            "Skalbarhet drift",
            "Informationssäkerhetsklassning",
            "Skalbarhet AI",
            "Funktionell bredd inom ILS",
            "Förmåga att tolka och hantera olika indataformat",
            "Supportkostnad",
            "Output - Struktur",
            "Grad av automation",
            "Time-to-deploy",
            "Systemintegration",
            "Robusthet",
            "Output - Filformat",
            "Användarvänlighet (UI/UX)",
            "Kundbas",
            "Utbildningsbehov",
            "Övrig funktionalitet"
        ]
    if 'vendor_list' not in st.session_state:
        st.session_state.vendor_list = ["Combitech", "Konkurrent A", "Konkurrent B"]
    if 'ratings_df' not in st.session_state:
        st.session_state.ratings_df = pd.DataFrame()
    if 'csf_order' not in st.session_state:
        st.session_state.csf_order = list(range(len(st.session_state.csf_list)))

def get_current_csf_data():
    """
    Hämta aktuell CSF-data med ROC-viktning
    
    How to modify:
    - Ändra viktberäkningen genom att byta ut calculate_roc_weights
    - Lägg till andra viktningsmetoder här
    """
    weights = calculate_roc_weights(len(st.session_state.csf_list), st.session_state.csf_order)
    
    csf_data = []
    for i, csf in enumerate(st.session_state.csf_list):
        csf_data.append({
            "name": csf,
            "weight": weights[i] if i < len(weights) else 0,
            "priority": st.session_state.csf_order[i] + 1 if i < len(st.session_state.csf_order) else i + 1
        })
    
    return csf_data

def initialize_ratings_dataframe():
    """
    Initialisera eller uppdatera ratings DataFrame
    
    How to modify:
    - Ändra default-värdet från 1 till önskat startvärde
    - Lägg till validering av betyg här
    """
    vendors = st.session_state.vendor_list
    csfs = st.session_state.csf_list
    
    # Skapa ny DataFrame med rätt struktur
    new_df = pd.DataFrame(index=vendors, columns=csfs)
    
    # Behåll befintliga värden om de finns
    if not st.session_state.ratings_df.empty:
        for vendor in vendors:
            for csf in csfs:
                if vendor in st.session_state.ratings_df.index and csf in st.session_state.ratings_df.columns:
                    new_df.loc[vendor, csf] = st.session_state.ratings_df.loc[vendor, csf]
                else:
                    new_df.loc[vendor, csf] = 1  # Default värde
    else:
        new_df = new_df.fillna(1).infer_objects(copy=False)  # Default värde för nya celler
    
    st.session_state.ratings_df = new_df

def calculate_cpm_results():
    """
    Beräkna viktade CPM-resultat baserat på aktuella betyg och ROC-vikter
    
    How to modify:
    - Ändra normaliseringsskalan från 0-100 till annat intervall
    - Lägg till fler beräkningsmetriker här
    """
    if st.session_state.ratings_df.empty:
        return pd.DataFrame()
    
    csf_data = get_current_csf_data()
    vendors = st.session_state.vendor_list
    
    results = []
    for vendor in vendors:
        raw_sum = 0
        weighted_sum = 0
        
        for csf in csf_data:
            if csf["name"] in st.session_state.ratings_df.columns:
                rating = st.session_state.ratings_df.loc[vendor, csf["name"]]
                raw_sum += rating
                weighted_sum += rating * csf["weight"]
        
        # Normaliserad poäng (0-100 skala)
        normalized_score = (weighted_sum / 4.0) * 100
        
        results.append({
            "Vendor": vendor,
            "Raw Sum": round(raw_sum, 2),
            "Weighted Sum": round(weighted_sum, 3),
            "Normalized (0-100)": round(normalized_score, 1)
        })
    
    return pd.DataFrame(results)

def create_cpm_bar_chart(results_df):
    """
    Skapa stapeldiagram över viktade CPM-resultat
    
    How to modify:
    - Ändra färger genom att ändra marker_color
    - Lägg till fler diagram-typer här
    """
    if results_df.empty:
        return None
    
    fig = go.Figure(data=[
        go.Bar(
            x=results_df['Vendor'],
            y=results_df['Normalized (0-100)'],
            text=results_df['Normalized (0-100)'],
            textposition='auto',
            marker_color='lightblue'
        )
    ])
    
    fig.update_layout(
        title="Viktade CPM-poäng (0-100 skala)",
        xaxis_title="Leverantör",
        yaxis_title="Poäng",
        showlegend=False,
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
        font=dict(color='white'),
        xaxis=dict(gridcolor='#333333', color='white'),
        yaxis=dict(gridcolor='#333333', color='white')
    )
    
    return fig

def create_cpm_heatmap():
    """
    Skapa heatmap över alla CPM-betyg
    
    How to modify:
    - Ändra färgskala från 'Viridis' till annan colorscale
    - Lägg till annotations genom att modifiera text-parametern
    """
    if st.session_state.ratings_df.empty:
        return None
    
    # Konvertera DataFrame till numeriskt format
    df_numeric = st.session_state.ratings_df.astype(float)
    
    fig = go.Figure(data=go.Heatmap(
        z=df_numeric.values,
        x=df_numeric.columns,
        y=df_numeric.index,
        colorscale='Viridis',
        text=df_numeric.values,
        texttemplate="%{text}",
        textfont={"size": 10},
        colorbar=dict(title="Betyg")
    ))
    
    fig.update_layout(
        title="Heatmap över alla CPM-betyg",
        xaxis_title="Kritiska Framgångsfaktorer",
        yaxis_title="Leverantörer",
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
        font=dict(color='white'),
        xaxis=dict(gridcolor='#333333', color='white'),
        yaxis=dict(gridcolor='#333333', color='white')
    )
    
    return fig

def show_cpm_tab():
    """
    Huvudfunktion för CPM-analys-fliken
    
    How to modify:
    - Lägg till fler konfigurationsalternativ i sidebaren
    - Ändra layout genom att modifiera kolumnstrukturen
    """
    st.header("📊 CPM-modell för ILS-mjukvaror")
    st.markdown("### Dynamisk ROC-analys med anpassningsbara CSF:er och leverantörer")
    
    st.markdown("""
    **Denna applikation erbjuder:**
    - Dynamiska CSF:er (lägg till/ta bort kritiska framgångsfaktorer)
    - Automatisk ROC-viktberäkning (Rank Order Centroid)
    - Flexibel leverantörslista
    - Realtidsuppdatering av resultat
    - Export till CSV för vidare analys
    """)
    
    # Sidebar för konfiguration
    with st.sidebar:
        st.header("⚙️ CPM Konfiguration")
        
        # CSF-hantering
        st.subheader("📋 Kritiska Framgångsfaktorer (CSF)")
        
        # Lägg till ny CSF
        new_csf = st.text_input("Lägg till ny CSF:")
        if st.button("➕ Lägg till CSF") and new_csf and new_csf not in st.session_state.csf_list:
            st.session_state.csf_list.append(new_csf)
            st.session_state.csf_order.append(len(st.session_state.csf_list) - 1)
            initialize_ratings_dataframe()
            st.success(f"Lade till: {new_csf}")
            st.rerun()
        
        # Ta bort CSF
        if len(st.session_state.csf_list) > 1:
            csf_to_remove = st.selectbox("Ta bort CSF:", [""] + st.session_state.csf_list)
            if st.button("🗑️ Ta bort CSF") and csf_to_remove:
                idx = st.session_state.csf_list.index(csf_to_remove)
                st.session_state.csf_list.remove(csf_to_remove)
                st.session_state.csf_order.pop(idx)
                # Justera ordningen för återstående CSF:er
                for i in range(len(st.session_state.csf_order)):
                    if st.session_state.csf_order[i] > idx:
                        st.session_state.csf_order[i] -= 1
                initialize_ratings_dataframe()
                st.success(f"Tog bort: {csf_to_remove}")
                st.rerun()
        
        st.divider()
        
        # Leverantörshantering
        st.subheader("🏢 Leverantörer")
        
        # Lägg till ny leverantör
        new_vendor = st.text_input("Lägg till ny leverantör:")
        if st.button("➕ Lägg till leverantör") and new_vendor and new_vendor not in st.session_state.vendor_list:
            st.session_state.vendor_list.append(new_vendor)
            initialize_ratings_dataframe()
            st.success(f"Lade till: {new_vendor}")
            st.rerun()
        
        # Ta bort leverantör
        if len(st.session_state.vendor_list) > 1:
            vendor_to_remove = st.selectbox("Ta bort leverantör:", [""] + st.session_state.vendor_list)
            if st.button("🗑️ Ta bort leverantör") and vendor_to_remove:
                st.session_state.vendor_list.remove(vendor_to_remove)
                initialize_ratings_dataframe()
                st.success(f"Tog bort: {vendor_to_remove}")
                st.rerun()
    
    # Huvudinnehåll
    initialize_ratings_dataframe()
    csf_data = get_current_csf_data()
    
    # Visa viktinformation
    st.subheader("⚖️ CSF-vikter (ROC-metoden)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Skapa DataFrame för viktvisning
        weights_df = pd.DataFrame([
            {"CSF": csf["name"], "Vikt": f"{csf['weight']:.4f}", "Prioritet": csf["priority"]}
            for csf in csf_data
        ])
        st.dataframe(weights_df, use_container_width=True)
    
    with col2:
        # Kontrollera vikternas summa
        total_weight = sum(csf["weight"] for csf in csf_data)
        if abs(total_weight - 1.0) < 0.001:
            st.success("✅ Vikternas summa är korrekt (1.0)")
        else:
            st.error(f"❌ Vikternas summa: {total_weight:.4f}")
    
    st.divider()
    
    # Betygsinmatning i matrisformat
    st.subheader("📝 Betygsinmatning (Matrisformat)")
    st.markdown("Ge betyg från 1 (sämst) till 4 (bäst) för varje kombination av leverantör och CSF.")
    
    # Skapa matris-layout
    # Header-rad med leverantörer
    header_cols = st.columns([2] + [1] * len(st.session_state.vendor_list))
    with header_cols[0]:
        st.markdown("**CSF**")
    for i, vendor in enumerate(st.session_state.vendor_list):
        with header_cols[i + 1]:
            st.markdown(f"**{vendor}**")
    
    # En rad per CSF
    for csf in csf_data:
        cols = st.columns([2] + [1] * len(st.session_state.vendor_list))
        
        # CSF-namn i första kolumnen
        with cols[0]:
            st.markdown(f"{csf['name'][:30]}{'...' if len(csf['name']) > 30 else ''}")
            st.caption(f"Vikt: {csf['weight']:.3f}")
        
        # Slider för varje leverantör
        for i, vendor in enumerate(st.session_state.vendor_list):
            with cols[i + 1]:
                current_rating = st.session_state.ratings_df.loc[vendor, csf["name"]]
                
                new_rating = st.slider(
                    label="Betyg",
                    min_value=1,
                    max_value=4,
                    value=int(current_rating),
                    step=1,
                    key=f"matrix_{vendor}_{csf['name']}",
                    label_visibility="collapsed"
                )
                
                # Visa beskrivning
                rating_descriptions = {1: "Dålig", 2: "Okej", 3: "Bra", 4: "Utmärkt"}
                st.caption(rating_descriptions[new_rating])
                
                # Uppdatera om ändrad
                if new_rating != current_rating:
                    st.session_state.ratings_df.loc[vendor, csf["name"]] = new_rating
                    st.rerun()
        
        st.divider()
    
    # Resultat och visualiseringar
    st.header("📈 CPM Resultat och Analys")
    
    results_df = calculate_cpm_results()
    
    if not results_df.empty:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📊 Sammanfattning")
            st.dataframe(results_df, use_container_width=True)
            
            # Export-knapp
            csv_data = export_to_csv(results_df, csf_data, st.session_state.ratings_df)
            st.download_button(
                label="📁 Exportera CPM-analys till CSV",
                data=csv_data,
                file_name="cpm_analys_resultat.csv",
                mime="text/csv"
            )
        
        with col2:
            st.subheader("📈 Stapeldiagram")
            chart = create_cpm_bar_chart(results_df)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
        
        # Heatmap
        st.subheader("🔥 Heatmap - Detaljvy av alla betyg")
        heatmap = create_cpm_heatmap()
        if heatmap:
            st.plotly_chart(heatmap, use_container_width=True)
    else:
        st.info("📝 Sätt betyg för leverantörerna för att se resultat.")
