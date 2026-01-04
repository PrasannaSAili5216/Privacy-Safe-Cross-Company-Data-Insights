import io
import pandas as pd
from src.fraud_analysis import compute_fraud_overlap, compute_inclusion_overlap, compute_trading_overlap

def fraud_excel(bank_df: pd.DataFrame, insurer_df: pd.DataFrame, epsilon: float = 1.0) -> bytes:
    buf = io.BytesIO()
    results = compute_fraud_overlap(bank_df, insurer_df, epsilon)
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        pd.DataFrame([results]).to_excel(writer, sheet_name="Summary", index=False)
        bank_df[bank_df["Is_Flagged_Fraud"] == 1][["Customer_ID_Hash", "Risk_Score"]].head(100).to_excel(writer, sheet_name="BankSample", index=False)
        insurer_df[insurer_df["Is_Flagged_Fraud"] == 1][["Customer_ID_Hash", "Claim_Amount"]].head(100).to_excel(writer, sheet_name="InsurerSample", index=False)
    buf.seek(0)
    return buf.read()

def inclusion_excel(bank_df: pd.DataFrame, insurer_df: pd.DataFrame, epsilon: float = 1.0) -> bytes:
    buf = io.BytesIO()
    results = compute_inclusion_overlap(bank_df, insurer_df, epsilon)
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        pd.DataFrame([results]).to_excel(writer, sheet_name="Summary", index=False)
        bank_df[bank_df["Credit_History_Months"] < 12][["Customer_ID_Hash", "Credit_History_Months"]].head(100).to_excel(writer, sheet_name="BankSample", index=False)
        insurer_df[insurer_df["Consistent_Payer"] == 1][["Customer_ID_Hash", "Consistent_Payer"]].head(100).to_excel(writer, sheet_name="InsurerSample", index=False)
    buf.seek(0)
    return buf.read()

def trading_excel(bank_df: pd.DataFrame, brokerage_df: pd.DataFrame, epsilon: float = 1.0) -> bytes:
    buf = io.BytesIO()
    results = compute_trading_overlap(bank_df, brokerage_df, epsilon)
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        pd.DataFrame([results]).to_excel(writer, sheet_name="Summary", index=False)
        brokerage_df[brokerage_df["Is_Risky_Trading"] == 1][["Customer_ID_Hash", "Portfolio_Value", "Trading_Frequency"]].head(100).to_excel(writer, sheet_name="BrokerSample", index=False)
        bank_df[bank_df["Is_Flagged_Fraud"] == 1][["Customer_ID_Hash", "Risk_Score"]].head(100).to_excel(writer, sheet_name="BankSample", index=False)
    buf.seek(0)
    return buf.read()
