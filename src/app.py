import streamlit as st
import pandas as pd
import altair as alt
import os
from src.data_gen import generate_bank_data, generate_insurer_data, generate_brokerage_data
from src.fraud_analysis import compute_fraud_overlap, compute_inclusion_overlap, compute_trading_overlap, simulate_cortex_chat
from src.export import fraud_excel, inclusion_excel, trading_excel
from src.utils import setup_logger

logger = setup_logger(__name__)

st.set_page_config(page_title="AI for Good: Privacy-Safe Insights", layout="wide")

def load_or_generate_data():
    """Loads data, generating it if missing or outdated (missing columns)."""
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    bank_path = os.path.join(data_dir, "bank_data.csv")
    insurer_path = os.path.join(data_dir, "insurer_data.csv")
    brokerage_path = os.path.join(data_dir, "brokerage_data.csv")
    
    regenerate = False
    
    if not os.path.exists(bank_path) or not os.path.exists(insurer_path) or not os.path.exists(brokerage_path):
        regenerate = True
    else:
        # Check for new columns
        df = pd.read_csv(bank_path, nrows=1)
        if 'Credit_History_Months' not in df.columns:
            regenerate = True
            
    if regenerate:
        st.warning("Generating new synthetic data with 'Financial Inclusion' fields...")
        bank_df = generate_bank_data("Global Bank", n_customers=1000, seed=10)
        insurer_df = generate_insurer_data("SafeGuard Insurance", n_customers=800, seed=20)
        brokerage_df = generate_brokerage_data("Alpha Brokerage", n_customers=900, seed=30)
        bank_df.to_csv(bank_path, index=False)
        insurer_df.to_csv(insurer_path, index=False)
        brokerage_df.to_csv(brokerage_path, index=False)
    else:
        bank_df = pd.read_csv(bank_path)
        insurer_df = pd.read_csv(insurer_path)
        brokerage_df = pd.read_csv(brokerage_path)
        
    return bank_df, insurer_df, brokerage_df

def main():
    st.title("🔒 Privacy-Safe Cross-Company Insights")
    st.markdown("""
    **Mission: Fraud Detection & Financial Inclusion without sharing raw customer data.
    """)

    # Load Data
    bank_df, insurer_df, brokerage_df = load_or_generate_data()
    
    # Sidebar Controls
    st.sidebar.header("🛡️ Privacy Controls")
    epsilon = st.sidebar.slider("Privacy Budget (Epsilon)", 0.1, 5.0, 1.0, 
                                help="Lower epsilon = More noise (Higher Privacy). Higher epsilon = More accuracy.")
    
    # Tabs for Use Cases
    tab1, tab2, tab3 = st.tabs(["🕵️ Fraud Detection", "🤝 Financial Inclusion (Credit Invisible)", "📈 Stock Market (Trading Risk)"])
    
    with tab1:
        st.subheader("Use Case: Collaborative Fraud Defense")
        st.info("Goal: Identify overlapping high-risk entities to stop cross-platform fraud.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Bank View (High Risk)")
            st.dataframe(bank_df[bank_df['Is_Flagged_Fraud']==1][['Customer_ID_Hash', 'Risk_Score']].head())
        with col2:
            st.caption("Insurer View (Flagged Claims)")
            st.dataframe(insurer_df[insurer_df['Is_Flagged_Fraud']==1][['Customer_ID_Hash', 'Claim_Amount']].head())
            
        if st.button("Run Secure Fraud Analysis", key="fraud_btn"):
            with st.spinner("Computing private intersection..."):
                results = compute_fraud_overlap(bank_df, insurer_df, epsilon=epsilon)
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Bank Risky", results['Bank Risky Count'])
                m2.metric("Insurer Risky", results['Insurer Risky Count'])
                m3.metric("⚠️ Overlapping Fraudsters", results['Private Overlap'], 
                          delta=f"True: {results['True Overlap']}", delta_color="off")
                
                chart_df = pd.DataFrame({
                    'Category': ['Bank Risky', 'Insurer Risky', 'Private Overlap', 'True Overlap'],
                    'Count': [results['Bank Risky Count'], results['Insurer Risky Count'], results['Private Overlap'], results['True Overlap']]
                })
                chart = alt.Chart(chart_df).mark_bar().encode(x='Category', y='Count', color='Category').properties(height=280)
                st.altair_chart(chart, width='stretch')
                dist_cols = st.columns(2)
                with dist_cols[0]:
                    bdist = alt.Chart(bank_df[bank_df['Is_Flagged_Fraud']==1]).mark_bar().encode(
                        alt.X('Risk_Score:Q', bin=alt.Bin(step=5), title='Risk Score (Bank Risky)'),
                        alt.Y('count()', title='Count')
                    ).properties(height=240)
                    st.altair_chart(bdist, width='stretch')
                with dist_cols[1]:
                    idist = alt.Chart(insurer_df[insurer_df['Is_Flagged_Fraud']==1]).mark_bar().encode(
                        alt.X('Claim_Amount:Q', bin=alt.Bin(maxbins=30), title='Claim Amount (Insurer Risky)'),
                        alt.Y('count()', title='Count')
                    ).properties(height=240)
                    st.altair_chart(idist, width='stretch')
                
                # Chat Simulation
                st.divider()
                st.markdown("#### 🤖 Cortex AI Analyst")
                q = st.text_input("Ask about fraud patterns:", "How many overlapping fraudsters did we find?", key="q1")
                if q:
                    st.write(simulate_cortex_chat(q, results))
                excel_bytes = fraud_excel(bank_df, insurer_df, epsilon)
                st.download_button("Download Excel (Fraud Analysis)", data=excel_bytes, file_name="fraud_analysis.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with tab2:
        st.subheader("Use Case: Spotting the 'Credit Invisible'")
        st.info("Goal: Find customers with thin credit history (Bank) but good payment history (Insurer) to offer loans.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Bank View (Thin Credit < 12mo)")
            st.dataframe(bank_df[bank_df['Credit_History_Months']<12][['Customer_ID_Hash', 'Credit_History_Months']].head())
        with col2:
            st.caption("Insurer View (Consistent Payers)")
            st.dataframe(insurer_df[insurer_df['Consistent_Payer']==1][['Customer_ID_Hash', 'Consistent_Payer']].head())
            
        if st.button("Run Financial Inclusion Analysis", key="inc_btn"):
            with st.spinner("Computing private intersection..."):
                results = compute_inclusion_overlap(bank_df, insurer_df, epsilon=epsilon)
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Bank 'Invisible'", results['Bank Invisible Count'])
                m2.metric("Insurer Good Payers", results['Insurer Good Payer Count'])
                m3.metric("🌟 Potential Candidates", results['Private Overlap'], 
                          delta=f"True: {results['True Overlap']}", delta_color="off")
                
                st.success(f"We found **{results['Private Overlap']}** candidates who deserve better credit offers!")

                chart_df = pd.DataFrame({
                    'Category': ['Bank Invisible', 'Insurer Good Payers', 'Private Overlap', 'True Overlap'],
                    'Count': [results['Bank Invisible Count'], results['Insurer Good Payer Count'], results['Private Overlap'], results['True Overlap']]
                })
                chart = alt.Chart(chart_df).mark_bar().encode(x='Category', y='Count', color='Category').properties(height=280)
                st.altair_chart(chart, width='stretch')
                dist_cols = st.columns(2)
                with dist_cols[0]:
                    hist = alt.Chart(bank_df).mark_bar().encode(
                        alt.X('Credit_History_Months:Q', bin=alt.Bin(step=3), title='Credit History Months (Bank)'),
                        alt.Y('count()', title='Count')
                    ).properties(height=240)
                    st.altair_chart(hist, width='stretch')
                with dist_cols[1]:
                    payer_df = insurer_df[['Consistent_Payer']].copy()
                    payer_df['Label'] = payer_df['Consistent_Payer'].map({1:'Consistent',0:'Inconsistent'})
                    payer_chart = alt.Chart(payer_df).mark_bar().encode(
                        x='Label:N',
                        y='count()',
                        color='Label:N'
                    ).properties(height=240)
                    st.altair_chart(payer_chart, width='stretch')

                # Chat Simulation
                st.divider()
                st.markdown("#### 🤖 Cortex AI Analyst")
                q = st.text_input("Ask about inclusion opportunities:", "How many credit invisible customers can we help?", key="q2")
                if q:
                    st.write(simulate_cortex_chat(q, results))
                excel_bytes = inclusion_excel(bank_df, insurer_df, epsilon)
                st.download_button("Download Excel (Financial Inclusion)", data=excel_bytes, file_name="inclusion_analysis.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with tab3:
        st.subheader("Use Case: Trading Risk Overlap")
        st.info("Goal: Identify customers with risky trading behavior who also have high bank risk.")
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Brokerage View (Risky Trading)")
            st.dataframe(brokerage_df[brokerage_df['Is_Risky_Trading']==1][['Customer_ID_Hash', 'Portfolio_Value', 'Trading_Frequency']].head())
        with col2:
            st.caption("Bank View (High Risk)")
            st.dataframe(bank_df[bank_df['Is_Flagged_Fraud']==1][['Customer_ID_Hash', 'Risk_Score']].head())
        if st.button("Run Trading Risk Analysis", key="trade_btn"):
            with st.spinner("Computing private intersection..."):
                results = compute_trading_overlap(bank_df, brokerage_df, epsilon=epsilon)
                m1, m2, m3 = st.columns(3)
                m1.metric("Brokerage Risky", results['Brokerage Risky Count'])
                m2.metric("Bank Risky", results['Bank Risky Count'])
                m3.metric("🔍 Overlapping Traders", results['Private Overlap'], delta=f"True: {results['True Overlap']}", delta_color="off")
                chart_df = pd.DataFrame({
                    'Category': ['Brokerage Risky', 'Bank Risky', 'Private Overlap', 'True Overlap'],
                    'Count': [results['Brokerage Risky Count'], results['Bank Risky Count'], results['Private Overlap'], results['True Overlap']]
                })
                chart = alt.Chart(chart_df).mark_bar().encode(x='Category', y='Count', color='Category').properties(height=280)
                st.altair_chart(chart, width='stretch')
                vis_cols = st.columns(2)
                with vis_cols[0]:
                    scatter = alt.Chart(brokerage_df[brokerage_df['Is_Risky_Trading']==1]).mark_circle(size=60).encode(
                        x=alt.X('Trading_Frequency:Q', title='Trading Frequency'),
                        y=alt.Y('Portfolio_Value:Q', title='Portfolio Value'),
                        tooltip=['Customer_ID_Hash','Trading_Frequency','Portfolio_Value']
                    ).properties(height=240)
                    st.altair_chart(scatter, width='stretch')
                with vis_cols[1]:
                    tf_hist = alt.Chart(brokerage_df).mark_bar().encode(
                        alt.X('Trading_Frequency:Q', bin=alt.Bin(step=2), title='Trading Frequency (All)'),
                        alt.Y('count()', title='Count')
                    ).properties(height=240)
                    st.altair_chart(tf_hist, width='stretch')
                st.divider()
                st.markdown("#### 🤖 Cortex AI Analyst")
                q = st.text_input("Ask about trading risk:", "How many overlapping risky traders did we find?", key="q3")
                if q:
                    st.write(simulate_cortex_chat(q, results))
                excel_bytes = trading_excel(bank_df, brokerage_df, epsilon)
                st.download_button("Download Excel (Trading Risk)", data=excel_bytes, file_name="trading_risk_analysis.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
if __name__ == "__main__":
    main()
