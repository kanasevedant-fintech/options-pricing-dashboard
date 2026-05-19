"""
app.py  —  Options Pricing & Greeks Dashboard
Run with: streamlit run app.py

Requires pricing.py, greeks.py, iv_solver.py in the same folder.
Tabs: Pricer & Greeks | Greek Profiles | IV Smile
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from pricing import bs_price
from greeks import delta, gamma, vega, theta, rho
from iv_solver import implied_vol

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Options Dashboard",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Options Pricing & Greeks Dashboard")
st.caption("Black-Scholes pricer · All five Greeks · Implied Volatility Smile")

# ── Sidebar inputs ────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Option Parameters")

    option_type = st.radio("Option type", ["call", "put"], horizontal=True)

    S = st.number_input("Spot price (S)", value=24_000.0, step=100.0)
    K = st.number_input("Strike price (K)", value=24_000.0, step=100.0)

    days = st.slider("Days to expiry", min_value=1, max_value=365, value=30)
    T = days / 365

    sigma = st.slider("Volatility (σ)  %", min_value=1, max_value=100, value=14) / 100
    r = st.slider("Risk-free rate (r)  %", min_value=0, max_value=15, value=7) / 100

    st.divider()
    st.caption(f"T = {T:.4f} years  ({days} days)")

# ── Compute ───────────────────────────────────────────────────────────────────
price   = bs_price(S, K, r, T, sigma, option_type)
d       = delta(S, K, r, T, sigma, option_type)
g       = gamma(S, K, r, T, sigma)
v       = vega(S, K, r, T, sigma)
th      = theta(S, K, r, T, sigma, option_type)
rh      = rho(S, K, r, T, sigma, option_type)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["💰 Pricer & Greeks", "📊 Greek Profiles", "🌊 IV Smile"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Price + Greek cards
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_price, col_space = st.columns([1, 3])
    with col_price:
        st.metric(
            label=f"{'Call' if option_type == 'call' else 'Put'} Price",
            value=f"₹ {price:,.2f}",
        )

    st.subheader("Greeks")
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Delta (Δ)", f"{d:.4f}",
              help="Price change per ₹1 move in spot. Range: 0 to 1 for calls, -1 to 0 for puts.")
    c2.metric("Gamma (Γ)", f"{g:.6f}",
              help="Rate of change of delta per ₹1 move in spot. Always positive for long options.")
    c3.metric("Vega (ν)", f"{v/100:.4f}",
              help="Price change per 1 vol-point (1%) change in σ.")
    c4.metric("Theta (Θ) /day", f"{th/365:.4f}",
              help="Daily time decay. Negative means the option loses this much per day.")
    c5.metric("Rho (ρ)", f"{rh/100:.4f}",
              help="Price change per 1 basis-point change in the risk-free rate.")

    st.subheader("Payoff at Expiry vs. Current Premium")

    spot_range = np.linspace(S * 0.7, S * 1.3, 300)

    if option_type == "call":
        payoff_at_expiry = np.maximum(spot_range - K, 0)
    else:
        payoff_at_expiry = np.maximum(K - spot_range, 0)

    pnl = payoff_at_expiry - price

    fig_payoff = go.Figure()
    fig_payoff.add_trace(go.Scatter(
        x=spot_range, y=payoff_at_expiry,
        name="Intrinsic value at expiry",
        line=dict(color="#1f77b4", width=2),
    ))
    fig_payoff.add_trace(go.Scatter(
        x=spot_range, y=pnl,
        name="Net P&L (after premium)",
        line=dict(color="#ff7f0e", width=2, dash="dash"),
    ))
    fig_payoff.add_hline(y=0, line_color="grey", line_dash="dot", line_width=1)
    fig_payoff.add_vline(x=K, line_color="red", line_dash="dot",
                         annotation_text="Strike", annotation_position="top left")
    fig_payoff.add_vline(x=S, line_color="green", line_dash="dot",
                         annotation_text="Spot", annotation_position="top right")
    fig_payoff.update_layout(
        title="Payoff Diagram",
        xaxis_title="Spot at Expiry",
        yaxis_title="₹ Profit / Loss",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=400,
    )
    st.plotly_chart(fig_payoff, use_container_width=True)

    with st.expander("🔍 Put-Call Parity Check"):
        call_p = bs_price(S, K, r, T, sigma, "call")
        put_p  = bs_price(S, K, r, T, sigma, "put")
        lhs = call_p - put_p
        rhs = S - K * np.exp(-r * T)
        st.write(f"**C − P** = {lhs:,.4f}")
        st.write(f"**S − K·e⁻ʳᵀ** = {rhs:,.4f}")
        st.write(f"Difference: {abs(lhs - rhs):.2e}  ✅" if abs(lhs - rhs) < 1e-6
                 else f"Difference: {abs(lhs - rhs):.4f}  ⚠️")
        st.caption("Put-call parity: C − P = S − K·e⁻ʳᵀ. Should hold to machine precision.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Greek profiles as spot moves
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("How Greeks Change as Spot Moves")
    st.caption("All other parameters held fixed at sidebar values.")

    spots = np.linspace(S * 0.70, S * 1.30, 300)

    greek_data = {
        "Delta":  [delta(s, K, r, T, sigma, option_type) for s in spots],
        "Gamma":  [gamma(s, K, r, T, sigma) for s in spots],
        "Vega":   [vega(s, K, r, T, sigma) / 100 for s in spots],
        "Theta":  [theta(s, K, r, T, sigma, option_type) / 365 for s in spots],
    }

    selected = st.multiselect(
        "Select Greeks to display",
        options=list(greek_data.keys()),
        default=["Delta", "Gamma"],
    )

    if selected:
        fig_greeks = go.Figure()
        colours = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
        for i, name in enumerate(selected):
            fig_greeks.add_trace(go.Scatter(
                x=spots, y=greek_data[name],
                name=name,
                line=dict(color=colours[i % 4], width=2),
            ))
        fig_greeks.add_vline(x=K, line_color="red", line_dash="dot",
                             annotation_text="Strike")
        fig_greeks.add_vline(x=S, line_color="green", line_dash="dot",
                             annotation_text="Current Spot")
        fig_greeks.update_layout(
            xaxis_title="Spot Price",
            yaxis_title="Greek Value",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            height=450,
        )
        st.plotly_chart(fig_greeks, use_container_width=True)

    st.subheader("Greeks at Current Parameters")
    table_data = {
        "Greek":       ["Delta (Δ)", "Gamma (Γ)", "Vega (ν) per vol-pt",
                        "Theta (Θ) per day", "Rho (ρ) per bp"],
        "Value":       [f"{d:.5f}", f"{g:.7f}", f"{v/100:.5f}",
                        f"{th/365:.5f}", f"{rh/100:.5f}"],
        "Meaning":     [
            "Option moves ₹{:.2f} for every ₹1 spot move".format(abs(d)),
            "Delta changes {:.5f} for every ₹1 spot move".format(g),
            "Option gains/loses ₹{:.4f} per 1% vol change".format(abs(v/100)),
            "Option loses ₹{:.4f} every day (time decay)".format(abs(th/365)),
            "Option changes ₹{:.4f} per 1bp rate change".format(abs(rh/100)),
        ],
    }
    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — IV Smile
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Implied Volatility Smile / Skew")

    st.info(
        "**What is the IV smile?**  Black-Scholes assumes a single constant "
        "volatility. But real markets price options at *different* implied "
        "volatilities across strikes. The pattern — usually a smirk for equity "
        "indices (higher IV for lower strikes) — reflects crash-risk fear. "
        "Plotting IV vs strike reveals this shape.",
        icon="💡",
    )

    st.caption(
        "Live NSE data not available in this environment. "
        "The chart below uses a **realistic synthetic NIFTY-like smile** "
        "parameterised by skew and curvature controls. "
        "Swap in real NSE option chain data by replacing `synthetic_chain()` "
        "with a pandas read of the NSE CSV download."
    )

    col_a, col_b, col_c = st.columns(3)
    atm_vol   = col_a.slider("ATM Volatility %", 8, 40, 14) / 100
    skew      = col_b.slider("Skew (left tail fear)", -0.20, 0.0, -0.07, step=0.01)
    curvature = col_c.slider("Curvature (smile bend)", 0.0, 1.0, 0.30, step=0.05)

    spot_smile = S

    def synthetic_chain(spot, atm_iv, skew, curvature, r, T):
        strikes = np.linspace(spot * 0.80, spot * 1.20, 25)
        rows = []
        for K_ in strikes:
            k = np.log(K_ / spot)
            iv = atm_iv + skew * k + curvature * k**2
            iv = max(iv, 0.01)
            call_p = bs_price(spot, K_, r, T, iv, "call")
            put_p  = bs_price(spot, K_, r, T, iv, "put")
            iv_rec_call = implied_vol(call_p, spot, K_, r, T, "call")
            iv_rec_put  = implied_vol(put_p,  spot, K_, r, T, "put")
            rows.append({
                "Strike":    round(K_),
                "Moneyness": f"{'ITM' if K_ < spot else 'OTM' if K_ > spot else 'ATM'} "
                             f"({k:+.3f})",
                "Input IV":  iv,
                "IV (Call)": iv_rec_call,
                "IV (Put)":  iv_rec_put,
                "Call Price": call_p,
                "Put Price":  put_p,
            })
        return pd.DataFrame(rows)

    df = synthetic_chain(spot_smile, atm_vol, skew, curvature, r, T)

    fig_smile = go.Figure()
    fig_smile.add_trace(go.Scatter(
        x=df["Strike"], y=df["IV (Call)"] * 100,
        name="Call IV", mode="lines+markers",
        line=dict(color="#1f77b4", width=2),
        marker=dict(size=6),
    ))
    fig_smile.add_trace(go.Scatter(
        x=df["Strike"], y=df["IV (Put)"] * 100,
        name="Put IV", mode="lines+markers",
        line=dict(color="#ff7f0e", width=2, dash="dash"),
        marker=dict(size=6),
    ))
    fig_smile.add_vline(x=spot_smile, line_color="green", line_dash="dot",
                        annotation_text="ATM (Spot)")
    fig_smile.update_layout(
        title="Implied Volatility Smile",
        xaxis_title="Strike Price",
        yaxis_title="Implied Volatility (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=420,
    )
    st.plotly_chart(fig_smile, use_container_width=True)

    st.subheader("IV Surface — Across Strikes and Expiries")
    st.caption("Each row is a different expiry. Drag to rotate in 3D.")

    expiry_days = [7, 14, 30, 45, 60, 90, 180]
    strike_range = np.linspace(S * 0.85, S * 1.15, 20)
    surface_z = []

    for exp in expiry_days:
        T_exp = exp / 365
        row = []
        for K_ in strike_range:
            k = np.log(K_ / S)
            iv = atm_vol + skew * k + curvature * k**2
            iv = max(iv, 0.01)
            row.append(iv * 100)
        surface_z.append(row)

    fig_surf = go.Figure(data=[go.Surface(
        x=strike_range,
        y=expiry_days,
        z=surface_z,
        colorscale="Viridis",
        colorbar=dict(title="IV %"),
    )])
    fig_surf.update_layout(
        scene=dict(
            xaxis_title="Strike",
            yaxis_title="Days to Expiry",
            zaxis_title="IV %",
        ),
        height=500,
    )
    st.plotly_chart(fig_surf, use_container_width=True)

    with st.expander("📋 Full Option Chain Data"):
        display_df = df[["Strike", "Moneyness", "IV (Call)", "IV (Put)",
                         "Call Price", "Put Price"]].copy()
        display_df["IV (Call)"] = (display_df["IV (Call)"] * 100).round(2).astype(str) + "%"
        display_df["IV (Put)"]  = (display_df["IV (Put)"]  * 100).round(2).astype(str) + "%"
        display_df["Call Price"] = display_df["Call Price"].round(2)
        display_df["Put Price"]  = display_df["Put Price"].round(2)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
