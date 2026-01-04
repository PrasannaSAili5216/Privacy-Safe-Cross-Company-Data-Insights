import pytest
import pandas as pd
import numpy as np
from src.privacy import add_laplace_noise, compute_private_mean, aggregate_insights

def test_add_laplace_noise_zero_epsilon():
    """Test that zero or negative epsilon returns the raw value (warning case)."""
    val = 100.0
    assert add_laplace_noise(val, epsilon=0) == val
    assert add_laplace_noise(val, epsilon=-1) == val

def test_add_laplace_noise_randomness():
    """Test that noise is actually added (probabilistic test)."""
    val = 100.0
    noisy_vals = [add_laplace_noise(val, epsilon=0.1) for _ in range(100)]
    # Check that not all values are equal to the original
    assert not all(v == val for v in noisy_vals)
    
def test_compute_private_mean_empty():
    """Test behavior on empty series."""
    s = pd.Series([], dtype=float)
    assert compute_private_mean(s) == 0.0

def test_compute_private_mean_bounds():
    """Test that the function runs without error on normal data."""
    s = pd.Series([10, 20, 30])
    mean = compute_private_mean(s, epsilon=1.0)
    assert isinstance(mean, float)

def test_aggregate_insights():
    """Test end-to-end aggregation."""
    df1 = pd.DataFrame({'Company': ['A']*10, 'Salary': np.random.rand(10)*100, 'Satisfaction': np.random.rand(10)*10})
    df2 = pd.DataFrame({'Company': ['B']*10, 'Salary': np.random.rand(10)*100, 'Satisfaction': np.random.rand(10)*10})
    
    results = aggregate_insights([df1, df2], epsilon=1.0)
    
    assert len(results) == 2
    assert results[0]['Company'] == 'A'
    assert results[1]['Company'] == 'B'
    assert 'Avg Salary (Private)' in results[0]
