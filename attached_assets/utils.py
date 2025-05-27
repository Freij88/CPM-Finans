"""
Utility functions for the CPM & Financial Analysis application.
These functions handle common operations like data processing and calculations.
"""

import pandas as pd
import numpy as np
import io

def calculate_roc_weights(n_csfs, order):
    """
    Beräkna ROC-vikter (Rank Order Centroid) för givna CSF:er
    
    Args:
        n_csfs: Antal CSF:er
        order: Lista med prioritetsordning (0-indexerad position för varje CSF)
    
    Returns:
        List med normaliserade vikter
        
    How to modify:
    - Ändra beräkningen genom att justera formeln på rad 25
    - För andra viktningsmetoder, ersätt hela funktionen
    """
    if n_csfs == 0:
        return []
    
    weights = []
    for i in range(n_csfs):
        # Ändrat från original: använd 1-baserad rankning
        rank = order[i] + 1  # Konvertera från 0-baserad till 1-baserad
        weight = sum(1/j for j in range(rank, n_csfs + 1)) / n_csfs
        weights.append(weight)
    
    # Normalisera så att summan blir 1
    total_weight = sum(weights)
    if total_weight > 0:
        weights = [w/total_weight for w in weights]
    
    return weights

def get_country_code(country_name):
    """
    Konvertera land till ISO-kod för visualisering
    
    How to modify:
    - Lägg till fler länder i country_mapping-dictionary
    - Ändra standardvärdet från 'N/A' till önskat värde
    """
    country_mapping = {
        'United States': 'USA',
        'United Kingdom': 'GBR', 
        'Sweden': 'SWE',
        'Germany': 'DEU',
        'France': 'FRA',
        'Canada': 'CAN',
        'Unknown': 'N/A'
    }
    return country_mapping.get(country_name, 'N/A')

def calculate_market_penetration(df, total_market_revenue=500):
    """
    Beräkna marknadspenetration baserat på total branschomsättning
    
    Args:
        df: DataFrame med finansiell data
        total_market_revenue: Total marknadsomsättning i miljarder USD
        
    How to modify:
    - Ändra total_market_revenue för din bransch
    - Lägg till fler beräkningar genom att utöka funktionen
    """
    if df.empty:
        return df
    
    df = df.copy()
    df['Market Penetration (%)'] = (df['Revenue (B USD)'] / total_market_revenue * 100).round(2)
    
    return df

def export_to_csv(results_df, csf_data, ratings_df):
    """
    Exportera alla CPM-data till CSV
    
    How to modify:
    - Ändra separator från ';' till ',' om önskad
    - Lägg till fler sektioner genom att utöka funktionen
    """
    output = io.StringIO()
    
    # Skriv CSF-vikter
    output.write("CSF-vikter (ROC-metoden)\n")
    output.write("CSF;Vikt;Prioritet\n")
    for csf in csf_data:
        output.write(f"{csf['name']};{csf['weight']:.4f};{csf['priority']}\n")
    
    output.write("\n")
    
    # Skriv detaljerade betyg
    output.write("Detaljerade betyg\n")
    ratings_df.to_csv(output, sep=';')
    
    output.write("\n")
    
    # Skriv resultat
    output.write("Sammanfattning av resultat\n")
    results_df.to_csv(output, index=False, sep=';')
    
    return output.getvalue()

def validate_uploaded_file(uploaded_file, required_columns):
    """
    Validera uppladdad fil och returnera DataFrame
    
    How to modify:
    - Lägg till fler filformat genom att utöka if-satsen
    - Ändra required_columns för olika användningsfall
    """
    if uploaded_file is None:
        return pd.DataFrame()
        
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            return pd.DataFrame()
        
        # Validera kolumner
        if all(col in df.columns for col in required_columns):
            return df
        else:
            return pd.DataFrame()
            
    except Exception:
        return pd.DataFrame()