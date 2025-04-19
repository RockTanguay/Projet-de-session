import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

# Configuration
st.set_page_config(layout="centered")
st.title("📊 Score d'Opportunité Boursière")

# Nouveaux paramètres sectoriels
SECTOR_GROWTH = {
    'Technology': 1.4,  # Multiplicateur de croissance
    'Healthcare': 1.3,
    'Communication Services': 1.2,
    'Consumer Cyclical': 1.1,
    'Financial Services': 1.0,
    'Industrials': 0.9,
    'Energy': 0.8,
    'Utilities': 0.7
}

# 1. Interface utilisateur
ticker = st.text_input("Symbole (ex: AAPL, SHOP.TO)", "TSLA").upper()

period_map = {
    "1 mois": "30d",
    "3 mois": "90d", 
    "6 mois": "180d",
    "1 an": "1y"
}
period_label = st.selectbox("Période d'analyse", list(period_map.keys()))
period = period_map[period_label]

if st.button("Analyser l'opportunité"):
    try:
        # 2. Récupération des données
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        
        if not info:
            raise ValueError("Symbole non reconnu")
            
        data = ticker_obj.history(period=period)
        
        if data.empty:
            st.error("Aucune donnée disponible")
        else:
            latest = data.iloc[-1]
            sector = info.get('sector', 'Unknown')
            
            # 3. Calcul des indicateurs (version améliorée)
            
            # Momentum (25%)
            momentum = (data['Close'][-1] - data['Close'][0]) / data['Close'][0] * 100
            momentum_score = min(25, max(0, 15 + momentum))
            
            # Volume (20%)
            avg_volume = data['Volume'].mean()
            volume_ratio = latest['Volume'] / avg_volume if avg_volume > 0 else 1
            volume_score = min(20, 12 * np.log1p(volume_ratio))
            
            # Support (15%)
            low_period = data['Close'].min()
            dist_support = max(0, (latest['Close'] - low_period) / low_period * 100)
            support_score = min(15, max(3, 15 - dist_support/4))
            
            # NOUVEAU: Croissance sectorielle (20%)
            growth_factor = SECTOR_GROWTH.get(sector, 1.0)
            growth_score = min(20, growth_factor * 15)  # Base 15 ajustée par secteur
            
            # NOUVEAU: Solidité financière (20%)
            financial_health = 0
            # Rentabilité
            if 'profitMargins' in info and info['profitMargins'] is not None:
                financial_health += info['profitMargins'] * 5  # Max 5 pts
            # Dette
            if 'debtToEquity' in info and info['debtToEquity'] is not None:
                financial_health += max(0, 10 - min(info['debtToEquity'], 5))  # Max 10 pts
            # Liquidité
            if 'currentRatio' in info and info['currentRatio'] is not None:
                financial_health += min(5, info['currentRatio'] * 2)  # Max 5 pts
            financial_score = min(20, financial_health)
            
            # Score total (0-100)
            total_score = int(momentum_score + volume_score + support_score + growth_score + financial_score)
            
            # 4. Affichage amélioré
            st.metric(
                "Score", 
                f"{total_score}/100",
                delta=f"{'📈 Excellente' if total_score >=85 else '👍 Bonne' if total_score >=70 else '⚠️ Moyenne' if total_score >=50 else '❌ Faible'} opportunité"
            )
            
            with st.expander("🔍 Détails complets"):
                cols = st.columns(2)
                cols[0].metric("Momentum", f"{momentum:.2f}%", f"{momentum_score}/25")
                cols[1].metric("Volume", f"{volume_ratio:.2f}x", f"{volume_score}/20")
                cols[0].metric("Support", f"{dist_support:.2f}%", f"{support_score}/15")
                cols[1].metric("Croissance secteur", sector, f"{growth_score}/20")
                cols[0].metric("Solidité financière", "", f"{financial_score}/20")
                
                # Analyse financière détaillée
                if 'profitMargins' in info:
                    cols[1].metric("Marge bénéfice", f"{info['profitMargins']*100:.1f}%")
                if 'debtToEquity' in info:
                    cols[0].metric("Dette/Capitaux", f"{info['debtToEquity']:.2f}")
                if 'currentRatio' in info:
                    cols[1].metric("Ratio courant", f"{info['currentRatio']:.2f}")
                
                st.line_chart(data['Close'])
                st.caption(f"Performance sur {period_label}")
            
            # Recommandation enrichie
            rec_col1, rec_col2 = st.columns([3, 1])
            with rec_col1:
                if financial_score >= 18:
                    st.success("💪 Très bonne santé financière")
                elif financial_score >= 12:
                    st.info("🆗 Santé financière correcte")
                else:
                    st.warning("🏥 Fragilité financière")
                    
                if growth_score >= 18:
                    st.success("🚀 Secteur à forte croissance")
                elif growth_score >= 12:
                    st.info("📈 Secteur en croissance modérée")
                else:
                    st.warning("🐌 Secteur à croissance lente")
            
            with rec_col2:
                if total_score >= 80:
                    st.success("✅ TRÈS BONNE OPPORTUNITÉ")
                elif total_score >= 60:
                    st.info("👍 CONSIDÉRER CE TITRE")
                else:
                    st.warning("⚠️ RISQUE ÉLEVÉ")

    except Exception as e:
        st.error(f"Erreur technique : {str(e)}")
        st.info("Conseils :\n- Vérifiez le format du symbole (ex: TSLA, SHOP.TO)\n- Essayez une période différente")