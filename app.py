import streamlit as st
import pandas as pd
from datetime import datetime
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpInteger, value, PULP_CBC_CMD

st.set_page_config(page_title="Print Optimizer", layout="wide")

SKUS = ["Bird", "Tree", "Sunset", "Railroad", "Airplane", "Stars", "Rhinoceros", "Peasant"]

COMBINATIONS = {
    "C1": {"skus": ["Bird", "Airplane", "Rhinoceros"], "cost": 10},
    "C2": {"skus": ["Stars", "Airplane"], "cost": 7},
    "C3": {"skus": ["Bird", "Tree", "Peasant", "Airplane"], "cost": 12},
    "C4": {"skus": ["Sunset", "Tree"], "cost": 6},
    "C5": {"skus": ["Tree", "Rhinoceros"], "cost": 9},
    "C6": {"skus": ["Railroad", "Rhinoceros", "Airplane", "Tree", "Stars"], "cost": 17},
}

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

st.title("Fabric Print Optimizer")
st.caption(f"Date: {datetime.now().strftime('%Y-%m-%d')}")

st.markdown("### Current Situation")

# Current Inventory
st.subheader("Current Inventory (beginning of this week)")

cols = st.columns(4)
inventory = {}
for i, sku in enumerate(SKUS):
    col = cols[i % 4]
    with col:
        inventory[sku] = st.number_input(sku, min_value=0, value=0, step=1, key=f"inv_{sku}")

st.markdown("**Current inventory summary**")
st.dataframe(pd.Series(inventory, name="Units").to_frame().style.format("{:,d}"), use_container_width=False)

# Last Week Actual Demand
st.subheader("Last Week Actual Demand (enter real numbers from last week)")

actual_last_week = {}
cols_actual = st.columns(4)
for i, sku in enumerate(SKUS):
    with cols_actual[i % 4]:
        actual_last_week[sku] = st.number_input(
            sku,
            min_value=0,
            value=0,
            step=1,
            key=f"actual_last_week_{sku}"
        )

st.markdown("**Last week actual summary**")
st.dataframe(pd.Series(actual_last_week, name="Units").to_frame().style.format("{:,d}"), use_container_width=False)

# Apply actuals
if st.button("Apply Last Week Actuals to Inventory", key="apply_actuals"):
    adjusted_inventory = {sku: inventory[sku] - actual_last_week[sku] for sku in SKUS}
    st.success("Adjusted inventory after subtracting last week's actual demand:")
    st.dataframe(pd.Series(adjusted_inventory, name="Adjusted Units").to_frame().style.format("{:,d}"), use_container_width=False)

# Editable Future Demand
st.subheader("Future Demand Forecast (next 7 weeks) – Edit as needed")

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
                    key=f"demand_{sku}_w{week}_{sku}"
                )
            )

if st.button("Preview Updated Demand", key="preview_demand_button"):
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

# Optimizer function
def run_optimizer(current_inventory, actual_last_week, demand_inputs, horizon=7):
    # Adjusted starting inventory
    start_inv = {sku: current_inventory[sku] - actual_last_week[sku] for sku in SKUS}

    # Demand from user inputs
    demand = pd.DataFrame(
        {sku: demand_inputs[sku] for sku in SKUS},
        index=list(range(1, horizon + 1))
    )

    prob = LpProblem("Print_Optimizer", LpMinimize)

    # Variables: x[c, w] = number of times combo c is printed in week w (w = 0 to horizon-1)
    x = LpVariable.dicts("x", ((c, w) for c in COMBINATIONS for w in range(horizon)), lowBound=0, cat=LpInteger)

    # Minimize total fabric cost
    prob += lpSum(x[c, w] * COMBINATIONS[c]["cost"] for c in COMBINATIONS for w in range(horizon))

    # Inventory balance constraints
    for sku in SKUS:
        # Week 1: start + production from week 0 >= demand week 1
        prod_w1 = lpSum(x[c, 0] for c in COMBINATIONS if sku in COMBINATIONS[c]["skus"])
        prob += start_inv[sku] + prod_w1 >= demand.loc[1, sku]

        # Weeks 2 to horizon
        for w in range(2, horizon + 1):
            prod_this = lpSum(x[c, w-1] for c in COMBINATIONS if sku in COMBINATIONS[c]["skus"])
            prev_inv = start_inv[sku] + lpSum(x[c, t] for c in COMBINATIONS if sku in COMBINATIONS[c]["skus"] for t in range(w-1)) - lpSum(demand.loc[t, sku] for t in range(1, w))
            prob += prev_inv + prod_this >= demand.loc[w, sku]

    # Min run size: if combo used in a week, at least 3
    for c in COMBINATIONS:
        for w in range(horizon):
            prob += x[c, w] >= 3 * (x[c, w] >= 1)  # indicator constraint

    # Max fabrics per week
    for w in range(horizon):
        prob += lpSum(x[c, w] for c in COMBINATIONS) <= 100

    # Solve
    prob.solve(PULP_CBC_CMD(msg=0))

    if prob.status != 1:
        return None, "No feasible solution found."

    # Production plan
    production = pd.DataFrame(
        {(c, w+1): value(x[c, w]) for c in COMBINATIONS for w in range(horizon)},
        index=["Quantity"]
    ).T
    production = production[production["Quantity"] > 0]

    # Inventory trajectory
    inventory_trajectory = pd.DataFrame(index=SKUS, columns=["Start"] + list(range(1, horizon+2)))
    inventory_trajectory["Start"] = start_inv.values()

    for w in range(1, horizon+2):
        for sku in SKUS:
            prod_this = sum(value(x[c, w-1]) for c in COMBINATIONS if sku in COMBINATIONS[c]["skus"]) if w <= horizon else 0
            prev = inventory_trajectory.at[sku, w-1] if w > 1 else start_inv[sku]
            inventory_trajectory.at[sku, w] = prev + prod_this - demand.loc[w, sku] if w <= horizon else prev + prod_this

    # Ending surplus value
    ending_inv = inventory_trajectory.iloc[:, -1]
    residual_value = sum(ending_inv[sku] * (10 if sku == "Rhinoceros" else 5) for sku in SKUS)

    total_cost = value(prob.objective)

    return {
        "production": production,
        "inventory_trajectory": inventory_trajectory,
        "total_cost": total_cost,
        "residual_value": residual_value
    }, None

# Run button
st.markdown("---")
if st.button("Run Optimization", type="primary"):
    with st.spinner("Optimizing production plan..."):
        result, error = run_optimizer(inventory, actual_last_week, demand_inputs)

    if error:
        st.error(error)
    else:
        st.success("Optimization complete!")

        st.subheader("Production Plan (combo quantities per week)")
        st.dataframe(result["production"])

        st.subheader("Projected Inventory Trajectory")
        st.dataframe(result["inventory_trajectory"].style.format("{:,.0f}"))

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Fabric Cost", f"${result['total_cost']:.2f}")
        with col2:
            st.metric("Ending Surplus Value", f"${result['residual_value']:.2f}")
