import pandas as pd
import numpy as np
import hashlib
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def hash_customer_id(customer_id: str) -> str:
    """Hashes a customer ID using SHA-256 for privacy."""
    return hashlib.sha256(customer_id.encode()).hexdigest()

def generate_bank_data(bank_name: str, n_customers: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Generates synthetic bank data including Risk Scores and Credit History."""
    np.random.seed(seed)
    
    # Generate fake IDs
    ids = [f"{bank_name}_CUST_{i:05d}" for i in range(n_customers)]
    hashed_ids = [hash_customer_id(i) for i in ids]
    
    # Risk Score (0-100), higher is riskier
    risk_scores = np.random.randint(0, 101, size=n_customers)
    
    # Credit History (Months) - Skewed low for "Credit Invisible" simulation
    credit_history_months = np.random.gamma(2, 10, size=n_customers).astype(int)
    
    # Fraud Flag (correlated with high risk)
    is_fraud = (risk_scores > 80) & (np.random.rand(n_customers) > 0.3)
    
    df = pd.DataFrame({
        'Customer_ID_Raw': ids,
        'Customer_ID_Hash': hashed_ids,
        'Risk_Score': risk_scores,
        'Credit_History_Months': credit_history_months,
        'Transaction_Volume': np.random.normal(5000, 2000, size=n_customers).round(2),
        'Is_Flagged_Fraud': is_fraud.astype(int)
    })
    
    logger.info(f"Generated {n_customers} records for {bank_name}")
    return df

def generate_insurer_data(insurer_name: str, n_customers: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Generates synthetic insurer data including Claims and Payment History."""
    np.random.seed(seed)
    
    ids = [f"{insurer_name}_CUST_{i:05d}" for i in range(n_customers)]
    # Create some overlap with Bank IDs for the simulation
    # We'll overlap the first 50% of IDs roughly
    overlap_count = int(n_customers * 0.5)
    bank_ids_overlap = [f"Global Bank_CUST_{i:05d}" for i in range(overlap_count)]
    final_ids = bank_ids_overlap + ids[overlap_count:]
    
    hashed_ids = [hash_customer_id(i) for i in final_ids]
    
    # Claims History
    claim_amount = np.random.exponential(1000, size=n_customers).round(2)
    
    # Good Payment History (for Credit Invisible use case)
    # 1 = Consistent Payer, 0 = Inconsistent
    consistent_payer = np.random.choice([0, 1], size=n_customers, p=[0.2, 0.8])
    
    # Fraud Flag
    is_fraud = (claim_amount > 5000) & (np.random.rand(n_customers) > 0.5)
    
    df = pd.DataFrame({
        'Customer_ID_Raw': final_ids,
        'Customer_ID_Hash': hashed_ids,
        'Claim_Amount': claim_amount,
        'Consistent_Payer': consistent_payer,
        'Is_Flagged_Fraud': is_fraud.astype(int)
    })
    
    logger.info(f"Generated {n_customers} records for {insurer_name}")
    return df

def generate_brokerage_data(broker_name: str, n_customers: int = 1000, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    ids = [f"{broker_name}_CUST_{i:05d}" for i in range(n_customers)]
    overlap_count = int(n_customers * 0.5)
    bank_ids_overlap = [f"Global Bank_CUST_{i:05d}" for i in range(overlap_count)]
    final_ids = bank_ids_overlap + ids[overlap_count:]
    hashed_ids = [hash_customer_id(i) for i in final_ids]
    portfolio_value = np.random.lognormal(mean=10, sigma=0.5, size=n_customers).round(2)
    trading_frequency = np.random.poisson(lam=20, size=n_customers)
    is_risky_trading = ((trading_frequency > 40) | (portfolio_value > np.percentile(portfolio_value, 95))) & (np.random.rand(n_customers) > 0.4)
    df = pd.DataFrame({
        'Customer_ID_Raw': final_ids,
        'Customer_ID_Hash': hashed_ids,
        'Portfolio_Value': portfolio_value,
        'Trading_Frequency': trading_frequency,
        'Is_Risky_Trading': is_risky_trading.astype(int)
    })
    logger.info(f"Generated {n_customers} records for {broker_name}")
    return df

if __name__ == "__main__":
    # Test generation
    logging.basicConfig(level=logging.INFO)
    generate_bank_data("TestBank")
    generate_insurer_data("TestInsurer")
    generate_brokerage_data("TestBroker")
