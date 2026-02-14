import streamlit as st
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(page_title="Print Optimizer", layout="wide")

# ── Data ────────────────────────────────────────────────────────────────

SKUS = ["Bird", "Tree", "Sunset", "Railroad", "Airplane", "Stars", "Rhinoceros", "Peasant"]

COMBINATIONS = {
    "C1": {"skus": ["Bird", "Airplane", "Rhinoceros"], "cost": 10},
    "C2": {"skus": ["Stars", "Airplane"], "cost": 7},
    "C3": {"skus": ["Bird", "Tree", "Peasant", "Airplane"], "cost": 12},
    "C4": {"skus": ["Sunset", "Tree"], "cost": 6},
    "C5": {"skus": ["Tree", "Rhinoceros"], "cost": 9},
    "C6": {"skus": ["Railroad", "Rhinoceros", "Airplane", "Tree", "Stars"], "cost": 17},
}

# Future demand forecast (weeks 1 to 7)
demand_data = {
    "Week": list(range(1, 8)),
    "Bird":      [3, 2, 0, 0, 7, 7, 0],
    "Tree":      [5, 5, 5, 5, 5, 5, 5],
    "Sunset":    [2, 2, 2, 4, 4, 4, 4],
    "Railroad":  [3, 3, 3, 3, 3, 3, 3],
    "Airplane":  [5, 5, 5, 8, 8,12, 5],
    "Stars":     [3, 3, 3, 3, 3, 3, 3],
    "Rhinoceros":[2, 2, 6, 6, 2, 2, 2],
    "Peasant":   [4, 4, 4, 3, 3, 3, 3],
}
future_demand = pd.DataFrame(demand_data).set_index("Week")

# ── UI ──────────────────────────────────────────────────────────────────

st.title("Fabric Print Optimizer")
st.caption(f"Date: {datetime.now().strftime('%Y-%m-%d')}")

st.markdown("### Current Situation")

# Current Inventory Inputs
st.subheader("Current Inventory (beginning of this week)")

cols = st.columns(4)
inventory = {}

for i, sku in enumerate(SKUS):
    col = cols[i % 4]
    with col:
        inventory[sku] = st.number_input(
            sku,
            min_value=0,
            value=0,
            step=1,
            key=f"inv_{sku}"
        )

st.markdown("**Summary of current inventory**")
st.dataframe(
    pd.Series(inventory, name="Units").to_frame().style.format("{:,d}"),
    use_container_width=False
)

# Demand Forecast Table
st.subheader("Future Demand Forecast (next 7 weeks)")
st.dataframe(future_demand.style.format("{:d}"), use_container_width=True)

# Combinations Reference
with st.expander("Available Combinations"):
    combo_rows = []
    for name, info in COMBINATIONS.items():
        combo_rows.append({
            "Combo": name,
            "SKUs": ", ".join(info["skus"]),
            "Cost per fabric": f"${info['cost']}"
        })
    st.dataframe(pd.DataFrame(combo_rows), use_container_width=True)

# Placeholder for Optimization
st.markdown("---")
if st.button("Run Optimization", type="primary"):
    st.info("Optimizer logic coming soon — this version shows data entry and UI only.")
    st.write("Current inventory values:", inventory)

st.markdown(
    """
    **Next steps planned:**
    - Input for actual demand from last week
    - PuLP optimization (min run 3, max 35 fabrics/week, lead time)
    - Projected inventory table
    - Cost & residual value summary
    """
)
