"""
pricing.py
----------
Black-Scholes option pricer.
"""

import numpy as np
from scipy.stats import norm


def compute_d1_d2(S, K, r, T, sigma):
    """
    Parameters
    ----------
    S     : float  — spot price
    K     : float  — strike price
    r     : float  — risk-free rate (annualised), e.g. 0.065
    T     : float  — time to expiry in YEARS, e.g. 30/365
    sigma : float  — volatility (annualised), e.g. 0.20

    Returns
    -------
    d1, d2 : (float, float)
    """
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2


def bs_price(S, K, r, T, sigma, option_type="call"):
    """
    Parameters
    ----------
    S, K, r, T, sigma : same as above
    option_type       : "call" or "put"

    Returns
    -------
    price : float
    """
    d1, d2 = compute_d1_d2(S, K, r, T, sigma)
    discount = np.exp(-r * T)

    if option_type == "call":
        price = S * norm.cdf(d1) - K * discount * norm.cdf(d2)
    else:
        price = K * discount * norm.cdf(-d2) - S * norm.cdf(-d1)

    return price


if __name__ == "__main__":
    S, K, r, T, sigma = 100, 100, 0.05, 1.0, 0.20
    call = bs_price(S, K, r, T, sigma, "call")
    put  = bs_price(S, K, r, T, sigma, "put")
    print(f"Call price : {call:.4f}   (expected ~10.45)")
    print(f"Put  price : {put:.4f}    (expected ~5.57)")
