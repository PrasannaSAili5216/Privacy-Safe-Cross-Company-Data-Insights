import os
import pandas as pd
from src.fraud_analysis import compute_fraud_overlap, compute_inclusion_overlap, compute_trading_overlap

def main():
    base = r"d:\Projects\Privacy-Safe Cross-Company Data Insights"
    data_dir = os.path.join(base, "data")
    out_dir = os.path.join(base, "powerbi")
    os.makedirs(out_dir, exist_ok=True)

    bank = pd.read_csv(os.path.join(data_dir, "bank_data.csv"))
    insurer = pd.read_csv(os.path.join(data_dir, "insurer_data.csv"))
    brokerage = pd.read_csv(os.path.join(data_dir, "brokerage_data.csv"))

    fraud = compute_fraud_overlap(bank, insurer, epsilon=1.0)
    inclusion = compute_inclusion_overlap(bank, insurer, epsilon=1.0)
    trading = compute_trading_overlap(bank, brokerage, epsilon=1.0)

    pd.DataFrame([fraud]).to_csv(os.path.join(out_dir, "fraud_summary.csv"), index=False)
    pd.DataFrame([inclusion]).to_csv(os.path.join(out_dir, "inclusion_summary.csv"), index=False)
    pd.DataFrame([trading]).to_csv(os.path.join(out_dir, "trading_summary.csv"), index=False)

    bank[['Customer_ID_Hash','Risk_Score','Credit_History_Months','Is_Flagged_Fraud']].to_csv(os.path.join(out_dir, "bank_customers.csv"), index=False)
    insurer[['Customer_ID_Hash','Claim_Amount','Consistent_Payer','Is_Flagged_Fraud']].to_csv(os.path.join(out_dir, "insurer_customers.csv"), index=False)
    brokerage[['Customer_ID_Hash','Portfolio_Value','Trading_Frequency','Is_Risky_Trading']].to_csv(os.path.join(out_dir, "brokerage_customers.csv"), index=False)

if __name__ == "__main__":
    main()
