"""
iv_solver.py
------------
Implied Volatility solver using Brent's method.
"""

import numpy as np
from scipy.optimize import brentq
from pricing import bs_price


def implied_vol(market_price, S, K, r, T, option_type="call"):
    """
    Compute implied volatility given a market-observed option price.

    Parameters
    ----------
    market_price : float  — the price observed in the market
    S, K, r, T   : same as before
    option_type  : "call" or "put"

    Returns
    -------
    iv : float or None
    """
    def f(sigma):
        return bs_price(S, K, r, T, sigma, option_type) - market_price

    try:
        return brentq(f, 1e-6, 10.0)
    except ValueError:
        return None


if __name__ == "__main__":
    S, K, r, T = 100, 100, 0.05, 1.0

    true_sigma = 0.20
    price = bs_price(S, K, r, T, true_sigma, "call")
    recovered = implied_vol(price, S, K, r, T, "call")
    print(f"Input sigma : {true_sigma:.4f}")
    print(f"Recovered IV: {recovered:.4f}  <- should match")

    print("\nIV across strikes (all priced at sigma=0.20, so all should recover 0.20):")
    for strike in [80, 90, 95, 100, 105, 110, 120]:
        p = bs_price(S, strike, r, T, true_sigma, "call")
        iv = implied_vol(p, S, strike, r, T, "call")
        print(f"  K={strike:3d}  price={p:.4f}  IV={iv:.4f}")
