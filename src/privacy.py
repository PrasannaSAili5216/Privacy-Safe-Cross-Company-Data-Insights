import numpy as np
import pandas as pd
from typing import List, Dict, Union, Any
from src.utils import setup_logger

logger = setup_logger(__name__)

def add_laplace_noise(value: float, epsilon: float = 1.0, sensitivity: float = 1.0) -> float:
    """
    Adds Laplace noise to a value for Differential Privacy.
    
    Args:
        value (float): The true value (e.g., sum, count).
        epsilon (float): Privacy budget (lower = more privacy, less accuracy).
        sensitivity (float): The maximum amount the value can change by adding/removing one individual.
    
    Returns:
        float: The noisy value.
    """
    if epsilon <= 0:
        logger.warning("Epsilon must be positive. Returning raw value (No Privacy!).")
        return value
        
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale)
    return value + noise

def compute_private_mean(series: pd.Series, epsilon: float = 1.0, lower_bound: float = 0, upper_bound: float = 200000) -> float:
    """
    Computes a differentially private mean.
    
    Args:
        series (pd.Series): The data series to compute the mean of.
        epsilon (float): Privacy budget.
        lower_bound (float): Lower clipping bound.
        upper_bound (float): Upper clipping bound.
        
    Returns:
        float: The differentially private mean.
    """
    if series.empty:
        logger.warning("Attempted to compute private mean of empty series. Returning 0.")
        return 0.0

    # Clip data to bounds to bound sensitivity
    clipped_series = series.clip(lower_bound, upper_bound)
    
    true_sum = float(clipped_series.sum())
    true_count = float(clipped_series.count())
    
    # Sensitivity for Sum is max(abs(lower_bound), abs(upper_bound)) - roughly the range width
    sum_sensitivity = max(abs(lower_bound), abs(upper_bound))
    # Sensitivity for Count is 1
    count_sensitivity = 1.0
    
    # Split epsilon budget between sum and count (half each)
    private_sum = add_laplace_noise(true_sum, epsilon/2, sum_sensitivity)
    private_count = add_laplace_noise(true_count, epsilon/2, count_sensitivity)
    
    if private_count <= 0:
        logger.debug(f"Private count <= 0 ({private_count}). Returning 0 to avoid division errors.")
        return 0.0 # Avoid division by zero or negative counts
        
    return private_sum / private_count

def aggregate_insights(dfs: List[pd.DataFrame], epsilon: float = 1.0) -> List[Dict[str, Any]]:
    """
    Aggregates insights from multiple dataframes privacy-safely.
    
    Args:
        dfs (List[pd.DataFrame]): List of company dataframes.
        epsilon (float): Privacy budget.
        
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing aggregated metrics.
    """
    results = []
    
    for i, df in enumerate(dfs):
        if df.empty:
            logger.warning(f"DataFrame at index {i} is empty. Skipping.")
            continue
            
        if 'Company' not in df.columns:
            logger.error(f"DataFrame at index {i} missing 'Company' column.")
            continue
            
        company_name = df['Company'].iloc[0]
        logger.info(f"Processing data for {company_name} with epsilon={epsilon}")
        
        # Calculate Private Metrics
        avg_salary = compute_private_mean(df['Salary'], epsilon=epsilon, upper_bound=150000)
        avg_satisfaction = compute_private_mean(df['Satisfaction'], epsilon=epsilon, upper_bound=10)
        
        results.append({
            'Company': company_name,
            'Avg Salary (Private)': avg_salary,
            'Avg Satisfaction (Private)': avg_satisfaction,
            'Avg Salary (True)': df['Salary'].mean(),
            'Avg Satisfaction (True)': df['Satisfaction'].mean()
        })
        
    return results
