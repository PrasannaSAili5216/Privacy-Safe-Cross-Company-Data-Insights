import pytest
import pandas as pd
from src.data_gen import generate_bank_data, generate_insurer_data, generate_brokerage_data
from src.fraud_analysis import compute_fraud_overlap, compute_inclusion_overlap, compute_trading_overlap

def test_data_generation_columns():
    """Test that generated data has correct columns for the new use case."""
    bank_df = generate_bank_data("Test Bank", n_customers=10)
    assert 'Customer_ID_Hash' in bank_df.columns
    assert 'Risk_Score' in bank_df.columns
    assert 'Is_Flagged_Fraud' in bank_df.columns
    assert 'Credit_History_Months' in bank_df.columns # New field

    insurer_df = generate_insurer_data("Test Insurer", n_customers=10)
    assert 'Customer_ID_Hash' in insurer_df.columns
    assert 'Claim_Amount' in insurer_df.columns
    assert 'Consistent_Payer' in insurer_df.columns # New field

def test_fraud_overlap_logic():
    """Test the logic for finding overlapping high-risk customers."""
    # Create manual data to ensure overlap
    bank_data = {
        'Customer_ID_Hash': ['hash1', 'hash2', 'hash3'],
        'Risk_Score': [90, 85, 20],  # hash1, hash2 are risky (>80)
        'Is_Flagged_Fraud': [1, 0, 0]
    }
    insurer_data = {
        'Customer_ID_Hash': ['hash1', 'hash2', 'hash4'],
        'Is_Flagged_Fraud': [1, 1, 0] # hash1, hash2 are flagged
    }
    
    df1 = pd.DataFrame(bank_data)
    df2 = pd.DataFrame(insurer_data)
    
    # Run analysis with epsilon=100 (low noise) to check logic
    results = compute_fraud_overlap(df1, df2, epsilon=100.0)
    
    # Overlap should be hash1 and hash2 (Both are risky in bank AND flagged in insurer)
    # Wait: 
    # Bank Risky: hash1 (90) - Wait, hash2 is not flagged in Is_Flagged_Fraud=0. 
    # Correction: In data_gen, Is_Flagged_Fraud depends on Risk_Score, but here I manually set it.
    # Logic uses Is_Flagged_Fraud column.
    # Bank Risky: hash1 (1). hash2 (0). hash3 (0). -> Only hash1.
    # Insurer Risky: hash1 (1), hash2 (1).
    # Intersection: hash1.
    
    # Let's fix the test data to be clearer
    bank_data = {
        'Customer_ID_Hash': ['A', 'B', 'C'],
        'Is_Flagged_Fraud': [1, 1, 0]
    }
    insurer_data = {
        'Customer_ID_Hash': ['A', 'B', 'D'],
        'Is_Flagged_Fraud': [1, 0, 1]
    }
    df1 = pd.DataFrame(bank_data)
    df2 = pd.DataFrame(insurer_data)
    
    results = compute_fraud_overlap(df1, df2, epsilon=100.0)
    # Bank: A, B
    # Insurer: A, D
    # Intersection: A
    assert results['True Overlap'] == 1

def test_inclusion_logic():
    """Test the 'Credit Invisible' logic."""
    # Bank: Low credit history (<12 months)
    bank_data = {
        'Customer_ID_Hash': ['A', 'B', 'C'],
        'Credit_History_Months': [5, 20, 2] # A and C are 'Invisible'
    }
    # Insurer: Good Payer (1)
    insurer_data = {
        'Customer_ID_Hash': ['A', 'B', 'C'],
        'Consistent_Payer': [1, 1, 0] # A and B are Good Payers
    }
    
    df1 = pd.DataFrame(bank_data)
    df2 = pd.DataFrame(insurer_data)
    
    results = compute_inclusion_overlap(df1, df2, epsilon=100.0)
    
    # Bank Invisible: A, C
    # Insurer Good: A, B
    # Intersection: A
    
    assert results['True Overlap'] == 1
    assert results['Bank Invisible Count'] == 2
    assert results['Insurer Good Payer Count'] == 2

def test_trading_overlap_logic():
    bank = pd.DataFrame({
        'Customer_ID_Hash': ['X', 'Y', 'Z'],
        'Is_Flagged_Fraud': [1, 0, 1]
    })
    broker = pd.DataFrame({
        'Customer_ID_Hash': ['X', 'A', 'B'],
        'Is_Risky_Trading': [1, 0, 1]
    })
    results = compute_trading_overlap(bank, broker, epsilon=100.0)
    assert results['True Overlap'] == 1
