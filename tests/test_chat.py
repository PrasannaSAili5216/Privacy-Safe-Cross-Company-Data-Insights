import pytest
from src.fraud_analysis import simulate_cortex_chat

def test_chat_fraud_overlap():
    results = {
        'Bank Risky Count': 10,
        'Insurer Risky Count': 8,
        'True Overlap': 3,
        'Private Overlap': 3.5
    }
    msg = simulate_cortex_chat("How many overlapping fraudsters did we find?", results)
    assert "3.5" in msg

def test_chat_inclusion_bank_invisible_count():
    results = {
        'Bank Invisible Count': 12,
        'Insurer Good Payer Count': 20,
        'True Overlap': 5,
        'Private Overlap': 5.2
    }
    msg = simulate_cortex_chat("Bank risky count", results)
    assert "Bank 'Invisible' count: 12." in msg

def test_chat_trading_overlap_specific():
    results = {
        'Bank Risky Count': 15,
        'Brokerage Risky Count': 9,
        'True Overlap': 4,
        'Private Overlap': 4.7
    }
    msg = simulate_cortex_chat("How many overlapping risky traders did we find?", results)
    assert "4.7" in msg

def test_chat_percentage_overlap():
    results = {
        'Bank Risky Count': 20,
        'Insurer Risky Count': 10,
        'True Overlap': 5,
        'Private Overlap': 5.1
    }
    msg = simulate_cortex_chat("What is the overlap percentage?", results)
    assert "Overlap share:" in msg

def test_chat_difference_accuracy():
    results = {
        'Bank Risky Count': 20,
        'Insurer Risky Count': 12,
        'True Overlap': 6,
        'Private Overlap': 7.0
    }
    msg = simulate_cortex_chat("What is the difference between private and true?", results)
    assert "Private vs true difference:" in msg

def test_chat_list_privacy_protection():
    results = {
        'Bank Risky Count': 10,
        'Insurer Risky Count': 8,
        'True Overlap': 3,
        'Private Overlap': 3.5
    }
    msg = simulate_cortex_chat("List the customer IDs", results)
    assert "Customer identities are not listed" in msg

def test_chat_download_guidance():
    results = {
        'Bank Risky Count': 10,
        'Insurer Risky Count': 8,
        'True Overlap': 3,
        'Private Overlap': 3.5
    }
    msg = simulate_cortex_chat("How to download Excel", results)
    assert "Use the Download buttons" in msg

def test_intent_overlap_synonyms():
    results = {
        'Bank Risky Count': 20,
        'Insurer Risky Count': 10,
        'True Overlap': 5,
        'Private Overlap': 5.1
    }
    msg = simulate_cortex_chat("Total overlapping entities", results)
    assert "Approximately" in msg

def test_intent_percentage_synonym_ratio():
    results = {
        'Bank Risky Count': 20,
        'Insurer Risky Count': 10,
        'True Overlap': 5,
        'Private Overlap': 5.1
    }
    msg = simulate_cortex_chat("Give me the overlap ratio", results)
    assert "Overlap share:" in msg

def test_intent_compare_vs_phrase():
    results = {
        'Bank Risky Count': 20,
        'Brokerage Risky Count': 15,
        'True Overlap': 4,
        'Private Overlap': 4.2
    }
    msg = simulate_cortex_chat("Compare bank vs brokerage", results)
    assert "Cohort sizes:" in msg
