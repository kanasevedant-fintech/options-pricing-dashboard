# Options Pricing & Greeks Dashboard

A Streamlit dashboard for pricing options using the Black-Scholes model, visualising all five Greeks, and exploring the Implied Volatility smile.

## Features

- **Pricer & Greeks** — Black-Scholes call/put price, all 5 Greeks (Delta, Gamma, Vega, Theta, Rho), payoff diagram, and put-call parity check
- **Greek Profiles** — interactive chart showing how each Greek changes as spot price moves
- **IV Smile** — synthetic IV smile with skew/curvature controls and a 3D IV surface across strikes and expiries

## Setup

```bash
pip install streamlit plotly pandas numpy scipy
streamlit run app.py
```

## File Structure

```
options_dashboard/
├── app.py          # Streamlit dashboard
├── pricing.py      # Black-Scholes pricer
├── greeks.py       # Delta, Gamma, Vega, Theta, Rho
└── iv_solver.py    # Implied Volatility via Brent's method
```
