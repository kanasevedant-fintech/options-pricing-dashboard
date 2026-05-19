"""
greeks.py
---------
The five option Greeks.
"""

import numpy as np
from scipy.stats import norm
from pricing import compute_d1_d2


def delta(S, K, r, T, sigma, option_type="call"):
    d1, _ = compute_d1_d2(S, K, r, T, sigma)
    if option_type == "call":
        return norm.cdf(d1)
    else:
        return norm.cdf(d1) - 1


def gamma(S, K, r, T, sigma):
    d1, _ = compute_d1_d2(S, K, r, T, sigma)
    return norm.pdf(d1) / (S * sigma * np.sqrt(T))


def vega(S, K, r, T, sigma):
    d1, _ = compute_d1_d2(S, K, r, T, sigma)
    return S * norm.pdf(d1) * np.sqrt(T)


def theta(S, K, r, T, sigma, option_type="call"):
    d1, d2 = compute_d1_d2(S, K, r, T, sigma)
    shared = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
    if option_type == "call":
        return shared - r * K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return shared + r * K * np.exp(-r * T) * norm.cdf(-d2)


def rho(S, K, r, T, sigma, option_type="call"):
    _, d2 = compute_d1_d2(S, K, r, T, sigma)
    if option_type == "call":
        return K * T * np.exp(-r * T) * norm.cdf(d2)
    else:
        return -K * T * np.exp(-r * T) * norm.cdf(-d2)


if __name__ == "__main__":
    S, K, r, T, sigma = 100, 100, 0.05, 1.0, 0.20

    print(f"Delta call : {delta(S, K, r, T, sigma, 'call'):.4f}  (expected  0.6368)")
    print(f"Delta put  : {delta(S, K, r, T, sigma, 'put'):.4f}  (expected -0.3632)")
    print(f"Gamma      : {gamma(S, K, r, T, sigma):.5f}  (expected  0.01876)")
    print(f"Vega       : {vega(S, K, r, T, sigma):.4f}  (expected 37.524)")
    print(f"Theta call : {theta(S, K, r, T, sigma, 'call'):.4f}  (expected -6.414)")
    print(f"Theta put  : {theta(S, K, r, T, sigma, 'put'):.4f}  (expected -1.658)")
    print(f"Rho call   : {rho(S, K, r, T, sigma, 'call'):.4f}  (expected 53.232)")
    print(f"Rho put    : {rho(S, K, r, T, sigma, 'put'):.4f}  (expected -41.890)")
