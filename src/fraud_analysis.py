import pandas as pd
import numpy as np
from src.privacy import add_laplace_noise
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

logger = logging.getLogger(__name__)

def compute_fraud_overlap(bank_df: pd.DataFrame, insurer_df: pd.DataFrame, epsilon: float = 1.0) -> dict:
    """
    Computes the intersection of high-risk customers from Bank and Insurer.
    Returns noisy counts to preserve privacy.
    """
    # 1. Local Filtering (simulating local compute)
    bank_risky = bank_df[bank_df['Is_Flagged_Fraud'] == 1]['Customer_ID_Hash']
    insurer_risky = insurer_df[insurer_df['Is_Flagged_Fraud'] == 1]['Customer_ID_Hash']
    
    # 2. Secure Intersection (PSI)
    # In a real clean room, this uses cryptographic PSI. Here we simulate it with set intersection on hashes.
    intersection = set(bank_risky).intersection(set(insurer_risky))
    true_overlap_count = len(intersection)
    
    # 3. Add Differential Privacy Noise
    # Sensitivity is 1 because one individual can change the count by at most 1
    private_overlap_count = add_laplace_noise(true_overlap_count, epsilon, sensitivity=1.0)
    
    # Ensure non-negative count (post-processing)
    private_overlap_count = max(0.0, private_overlap_count)
    
    return {
        'Bank Risky Count': len(bank_risky),
        'Insurer Risky Count': len(insurer_risky),
        'True Overlap': true_overlap_count,
        'Private Overlap': round(private_overlap_count, 1)
    }

def compute_inclusion_overlap(bank_df: pd.DataFrame, insurer_df: pd.DataFrame, epsilon: float = 1.0) -> dict:
    """
    Computes the intersection of 'Credit Invisible' customers (Bank) 
    who are 'Consistent Payers' (Insurer).
    """
    # 1. Bank finds "Credit Invisible" (e.g., < 12 months history)
    bank_invisible = bank_df[bank_df['Credit_History_Months'] < 12]['Customer_ID_Hash']
    
    # 2. Insurer finds "Consistent Payers"
    insurer_good = insurer_df[insurer_df['Consistent_Payer'] == 1]['Customer_ID_Hash']
    
    # 3. Secure Intersection
    intersection = set(bank_invisible).intersection(set(insurer_good))
    true_overlap_count = len(intersection)
    
    # 4. Add Privacy Noise
    private_overlap_count = add_laplace_noise(true_overlap_count, epsilon, sensitivity=1.0)
    private_overlap_count = max(0.0, private_overlap_count)
    
    return {
        'Bank Invisible Count': len(bank_invisible),
        'Insurer Good Payer Count': len(insurer_good),
        'True Overlap': true_overlap_count,
        'Private Overlap': round(private_overlap_count, 1)
    }

def compute_trading_overlap(bank_df: pd.DataFrame, brokerage_df: pd.DataFrame, epsilon: float = 1.0) -> dict:
    bank_risky = bank_df[bank_df['Is_Flagged_Fraud'] == 1]['Customer_ID_Hash']
    broker_risky = brokerage_df[brokerage_df['Is_Risky_Trading'] == 1]['Customer_ID_Hash']
    intersection = set(bank_risky).intersection(set(broker_risky))
    true_overlap_count = len(intersection)
    private_overlap_count = add_laplace_noise(true_overlap_count, epsilon, sensitivity=1.0)
    private_overlap_count = max(0.0, private_overlap_count)
    return {
        'Bank Risky Count': len(bank_risky),
        'Brokerage Risky Count': len(broker_risky),
        'True Overlap': true_overlap_count,
        'Private Overlap': round(private_overlap_count, 1)
    }

def _classify_intent(q: str) -> str:
    intents = {
        'overlap_count': [
            'how many overlap', 'total overlapping', 'number of overlapping', 'intersect count', 'common entities'
        ],
        'bank_count': [
            'bank risky count', 'bank invisible count', 'how many bank risky'
        ],
        'partner_count': [
            'insurer risky count', 'insurer good payers count', 'brokerage risky count'
        ],
        'percentage': [
            'overlap percentage', 'ratio', 'share', 'portion', 'rate'
        ],
        'difference': [
            'difference between private and true', 'accuracy delta', 'noise difference'
        ],
        'privacy': [
            'explain epsilon', 'privacy budget', 'laplace noise', 'noise'
        ],
        'compare': [
            'compare bank vs insurer', 'bank vs brokerage', 'compare cohorts', 'vs'
        ],
        'export': [
            'download excel', 'power bi export', 'csv export', 'export data'
        ],
        'trading': [
            'risky traders', 'trading overlap', 'trader overlap'
        ],
        'fraud': [
            'overlapping fraudsters', 'fraud overlap', 'fraud count'
        ],
        'inclusion': [
            'credit invisible', 'inclusion overlap', 'inclusion candidates'
        ]
    }
    phrases = []
    labels = []
    for k, v in intents.items():
        for p in v:
            phrases.append(p)
            labels.append(k)
    vec = TfidfVectorizer().fit(phrases)
    X = vec.transform(phrases)
    y = labels
    qv = vec.transform([q])
    sims = linear_kernel(qv, X).flatten()
    i = int(np.argmax(sims))
    if sims[i] >= 0.2:
        return y[i]
    return ''

def simulate_cortex_chat(user_query: str, analysis_results: dict) -> str:
    query_lower = user_query.lower()
    private_overlap = analysis_results.get('Private Overlap')
    true_overlap = analysis_results.get('True Overlap')
    bank_risky = analysis_results.get('Bank Risky Count')
    insurer_risky = analysis_results.get('Insurer Risky Count')
    bank_invisible = analysis_results.get('Bank Invisible Count')
    insurer_good = analysis_results.get('Insurer Good Payer Count')
    brokerage_risky = analysis_results.get('Brokerage Risky Count')
    context = 'fraud' if insurer_risky is not None else 'inclusion' if insurer_good is not None else 'trading' if brokerage_risky is not None else 'generic'
    intent = _classify_intent(query_lower)
    if intent == 'overlap_count':
        if context == 'fraud':
            return f"Approximately {private_overlap} overlapping high-risk entities were identified across bank and insurer."
        if context == 'inclusion':
            return f"Approximately {private_overlap} customers meet inclusion criteria across bank and insurer."
        if context == 'trading':
            return f"Approximately {private_overlap} overlapping risky traders were identified across bank and brokerage."
        return f"Approximately {private_overlap} overlapping entities were identified."
    if intent == 'percentage':
        a = bank_risky if bank_risky is not None else bank_invisible
        b = insurer_risky if insurer_risky is not None else insurer_good if insurer_good is not None else brokerage_risky
        if true_overlap is not None and a and b:
            p_bank = round(100.0 * true_overlap / a, 1) if a > 0 else 0.0
            p_partner = round(100.0 * true_overlap / b, 1) if b > 0 else 0.0
            return f"Overlap share: {p_bank}% of bank cohort; {p_partner}% of partner cohort."
        return "Overlap percentage unavailable due to missing totals."
    if intent == 'difference':
        if private_overlap is not None and true_overlap is not None:
            d = round(private_overlap - true_overlap, 1)
            return f"Private vs true difference: {d}. Differential privacy adds noise to protect identities."
        return "Accuracy comparison unavailable without both private and true counts."
    if intent == 'privacy':
        return "Epsilon controls privacy noise. Lower values add more noise and increase privacy; higher values reduce noise and increase accuracy. Counts shown as 'Private Overlap' include Laplace noise."
    if intent == 'compare':
        a = bank_risky if bank_risky is not None else bank_invisible
        b = insurer_risky if insurer_risky is not None else insurer_good if insurer_good is not None else brokerage_risky
        if a is not None and b is not None:
            return f"Cohort sizes: Bank={a}, Partner={b}. True overlap={true_overlap}, Private overlap={private_overlap}."
        return "Comparison unavailable due to missing cohort sizes."
    if intent == 'export':
        return "Use the Download buttons in each tab to export Excel summaries, or refer to the Power BI CSVs in the powerbi folder."
    if intent == 'trading':
        if private_overlap is not None:
            return f"Overlapping risky traders: {private_overlap}. True overlap: {true_overlap}."
        return "Trading risk overlap not available. Run the Trading Risk Analysis."
    if intent == 'fraud':
        if private_overlap is not None:
            return f"Overlapping fraudsters: {private_overlap}. True overlap: {true_overlap}."
        return "Fraud overlap not available. Run the Fraud Analysis."
    if intent == 'inclusion':
        if private_overlap is not None:
            return f"Potential inclusion candidates: {private_overlap}. True overlap: {true_overlap}."
        return "Inclusion overlap not available. Run the Financial Inclusion Analysis."
    if any(x in query_lower for x in ["how many", "count", "number", "how much", "total"]) and any(x in query_lower for x in ["overlap", "overlapping", "intersect", "common", "shared", "match"]):
        if context == 'fraud':
            return f"Approximately {private_overlap} overlapping high-risk entities were identified across bank and insurer."
        if context == 'inclusion':
            return f"Approximately {private_overlap} customers meet inclusion criteria across bank and insurer."
        if context == 'trading':
            return f"Approximately {private_overlap} overlapping risky traders were identified across bank and brokerage."
        return f"Approximately {private_overlap} overlapping entities were identified."
    if "difference" in query_lower or "delta" in query_lower or "accur" in query_lower or "confidence" in query_lower:
        if private_overlap is not None and true_overlap is not None:
            d = round(private_overlap - true_overlap, 1)
            return f"Private vs true difference: {d}. Differential privacy adds noise to protect identities."
        return "Accuracy comparison unavailable without both private and true counts."
    if "trading" in query_lower or "trader" in query_lower:
        if private_overlap is not None:
            return f"Overlapping risky traders: {private_overlap}. True overlap: {true_overlap}."
        return "Trading risk overlap not available. Run the Trading Risk Analysis."
    if "fraud" in query_lower or "fraudster" in query_lower:
        if private_overlap is not None:
            return f"Overlapping fraudsters: {private_overlap}. True overlap: {true_overlap}."
        return "Fraud overlap not available. Run the Fraud Analysis."
    if "credit" in query_lower or "invisible" in query_lower or "inclusion" in query_lower:
        if private_overlap is not None:
            return f"Potential inclusion candidates: {private_overlap}. True overlap: {true_overlap}."
        return "Inclusion overlap not available. Run the Financial Inclusion Analysis."
    if "bank" in query_lower and "risk" in query_lower:
        c = bank_risky if context != 'inclusion' else bank_invisible
        label = "Bank Risky" if context != 'inclusion' else "Bank 'Invisible'"
        if c is not None:
            return f"{label} count: {c}."
    if "insurer" in query_lower:
        c = insurer_risky if context == 'fraud' else insurer_good
        label = "Insurer Risky" if context == 'fraud' else "Insurer Good Payers"
        if c is not None:
            return f"{label} count: {c}."
    if "broker" in query_lower or "brokerage" in query_lower:
        if brokerage_risky is not None:
            return f"Brokerage Risky count: {brokerage_risky}."
    if "percent" in query_lower or "%" in query_lower or "rate" in query_lower or "ratio" in query_lower or "share" in query_lower or "portion" in query_lower:
        a = bank_risky if bank_risky is not None else bank_invisible
        b = insurer_risky if insurer_risky is not None else insurer_good if insurer_good is not None else brokerage_risky
        if true_overlap is not None and a and b:
            p_bank = round(100.0 * true_overlap / a, 1) if a > 0 else 0.0
            p_partner = round(100.0 * true_overlap / b, 1) if b > 0 else 0.0
            return f"Overlap share: {p_bank}% of bank cohort; {p_partner}% of partner cohort."
        return "Overlap percentage unavailable due to missing totals."
    if "epsilon" in query_lower or "privacy" in query_lower or "noise" in query_lower:
        return "Epsilon controls privacy noise. Lower values add more noise and increase privacy; higher values reduce noise and increase accuracy. Counts shown as 'Private Overlap' include Laplace noise."
    if "who" in query_lower or "which customer" in query_lower or "list" in query_lower or "ids" in query_lower:
        return "Customer identities are not listed to protect privacy. The system only reports aggregate overlaps."
    if "download" in query_lower or "excel" in query_lower or "power bi" in query_lower or "csv" in query_lower:
        return "Use the Download buttons in each tab to export Excel summaries, or refer to the provided Power BI CSVs."
    if "explain" in query_lower or "what is" in query_lower:
        if context == 'fraud':
            return "Fraud overlap measures customers flagged by both bank and insurer. It is computed via hash intersection and protected with differential privacy."
        if context == 'inclusion':
            return "Inclusion overlap measures thin-credit bank customers who are consistent payers at the insurer, protected with differential privacy."
        if context == 'trading':
            return "Trading overlap measures risky bank customers who also exhibit risky trading behavior at the brokerage, protected with differential privacy."
        return "The analysis uses privacy-preserving intersections and adds Laplace noise to protect individual data contributions."
    if "compare" in query_lower or "vs" in query_lower:
        a = bank_risky if bank_risky is not None else bank_invisible
        b = insurer_risky if insurer_risky is not None else insurer_good if insurer_good is not None else brokerage_risky
        if a is not None and b is not None:
            return f"Cohort sizes: Bank={a}, Partner={b}. True overlap={true_overlap}, Private overlap={private_overlap}."
        return "Comparison unavailable due to missing cohort sizes."
    return "You can ask about overlaps, counts, percentages, differences, comparisons, privacy, or exports."
