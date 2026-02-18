import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Print Optimizer", layout="wide")

# SKUs and combinations (unchanged)
SKUS = ["Bird", "Tree", "Sunset", "Railroad", "Airplane", "Stars", "Rhinoceros", "Peasant"]

COMBINATIONS = {
    "C1": {"skus": ["Bird", "Airplane", "Rhinoceros"], "cost": 10},
    "C2": {"skus": ["Stars", "Airplane"], "cost": 7},
    "C3": {"skus": ["Bird", "Tree", "Peasant", "Airplane"], "cost": 12},
    "C4": {"skus": ["Sunset", "Tree"], "cost": 6},
    "C5": {"skus": ["Tree", "Rhinoceros"], "cost": 9},
    "C6": {"skus": ["Railroad", "Rhinoceros", "Airplane", "Tree", "Stars"], "cost": 17},
}

# Editable future demand forecast with simple number inputs
# Editable future demand forecast with simple number inputs
st.subheader("Future Demand Forecast (next 7 weeks) – Edit as needed")

# Hardcoded defaults (moved here so we don't depend on removed future_demand)
default_demand = {
    "Bird": [3, 2, 0, 0, 7, 7, 0],
    "Tree": [5, 5, 5, 5, 5, 5, 5],
    "Sunset": [2, 2, 2, 4, 4, 4, 4],
    "Railroad": [3, 3, 3, 3, 3, 3, 3],
    "Airplane": [5, 5, 5, 8, 8, 12, 5],
    "Stars": [3, 3, 3, 3, 3, 3, 3],
    "Rhinoceros": [2, 2, 6, 6, 2, 2, 2],
    "Peasant": [4, 4, 4, 3, 3, 3, 3],
}

demand_inputs = {}
for sku in SKUS:
    st.markdown(f"**{sku}**")
    demand_inputs[sku] = []
    cols = st.columns(7)
    for week in range(1, 8):
        with cols[week - 1]:
            default_value = default_demand.get(sku, [0] * 7)[week - 1]
            demand_inputs[sku].append(
                st.number_input(
                    f"Week {week}",
                    min_value=0,
                    value=int(default_value),
                    step=1,
                    key=f"demand_{sku}_week{week}"
                )
            )

# Preview button
if st.button("Preview Updated Demand", key="preview_demand"):
    updated_demand = pd.DataFrame(
        {sku: demand_inputs[sku] for sku in SKUS},
        index=list(range(1, 8))
    )
    st.dataframe(updated_demand.style.format("{:d}"), use_container_width=True)



# UI
st.title("Fabric Print Optimizer")
st.caption(f"Date: {datetime.now().strftime('%Y-%m-%d')}")

st.markdown("### Current Situation")

# Current Inventory (unchanged)
st.subheader("Current Inventory (beginning of this week)")

cols = st.columns(4)
inventory = {}
for i, sku in enumerate(SKUS):
    col = cols[i % 4]
    with col:
        inventory[sku] = st.number_input(sku, min_value=0, value=0, step=1, key=f"inv_{sku}")

st.markdown("**Current inventory summary**")
st.dataframe(pd.Series(inventory, name="Units").to_frame().style.format("{:,d}"), use_container_width=False)

# Editable Future Demand Forecast
st.subheader("Future Demand Forecast (next 7 weeks) – Edit as needed")

# Hardcoded defaults (safe fallback, no DataFrame needed)
default_demand = {
    "Bird": [3, 2, 0, 0, 7, 7, 0],
    "Tree": [5, 5, 5, 5, 5, 5, 5],
    "Sunset": [2, 2, 2, 4, 4, 4, 4],
    "Railroad": [3, 3, 3, 3, 3, 3, 3],
    "Airplane": [5, 5, 5, 8, 8, 12, 5],
    "Stars": [3, 3, 3, 3, 3, 3, 3],
    "Rhinoceros": [2, 2, 6, 6, 2, 2, 2],
    "Peasant": [4, 4, 4, 3, 3, 3, 3],
}

demand_inputs = {}
for sku in SKUS:
    st.markdown(f"**{sku}**")
    demand_inputs[sku] = []
    cols = st.columns(7)
    for week in range(1, 8):
        with cols[week - 1]:
            default_value = default_demand.get(sku, [0] * 7)[week - 1]
            demand_inputs[sku].append(
                st.number_input(
                    f"Week {week}",
                    min_value=0,
                    value=int(default_value),
                    step=1,
                    key=f"demand_{sku}_week{week}"
                )
            )

# Preview button to see edited values in table form
if st.button("Preview Updated Demand", key="preview_demand"):
    updated_demand = pd.DataFrame(
        {sku: demand_inputs[sku] for sku in SKUS},
        index=list(range(1, 8))
    )
    st.dataframe(updated_demand.style.format("{:d}"), use_container_width=True)

with st.expander("Available Combinations (reference)"):
    combo_rows = []
    for name, info in COMBINATIONS.items():
        combo_rows.append({
            "Combo": name,
            "SKUs": ", ".join(info["skus"]),
            "Cost per fabric": f"${info['cost']}"
        })
    st.dataframe(pd.DataFrame(combo_rows), use_container_width=True)

st.markdown("---")
if st.button("Run Optimization", type="primary"):
    st.info("Optimizer not yet implemented — this version allows editing demand and inventory.")
    st.write("Current inventory:", inventory)
