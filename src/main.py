import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent.parent
EXPENDITURES_PATH = ROOT / "expenditures.csv"
DEPOSITS_PATH = ROOT / "deposits.csv"

EXPENDITURE_CATEGORIES = [
    "transport",
    "groceries",
    "health and wellness",
    "utilities",
    "home",
    "automotive",
    "pharmacy",
    "eating out",
    "shopping",
    "services",
    "insurance",
    "religious",
    "tax"
]

ALL_SUBCATEGORIES = [
    "transport:public transit",
    "transport:gas",
    "transport:tolls",
    "transport:parking",
    "automotive:parts/fluids",
    "groceries:staples",
    "groceries:coffee",
    "health and wellness:supplements",
    "health and wellness:gym",
    "utilities:phone",
    "utilities:electric",
    "utilities:internet",
    "utilities:compost",
    "utilities:AI subscription",
    "utilities:water",
    "utilities:gas",
    "utilities:HOA",
    "eating out:coffee",
    "eating out:treats",
    "eating out:restaurant",
    "shopping:clothes",
    "shopping:appliances",
    "shopping:tools",
    "shopping:office",
    "services:cleaners",
    "insurance:home",
    "insurance:auto",
    "insurance:health/life",
    "religious:candles",
    "religious:donation",
    "tax:payments",
    "tax:software",
    "pharmacy"
]

MERCHANTS = [
    "Tonys",
    "Whole Foods",
    "Costco",
    "Home Depot",
    "Aldi",
    "Backlot",
    "Unique",
    "Metric",
]

NECESSITY = [
    "basic",
    "middle",
    "luxury",
    "donation"
]

DEPOSIT_CATEGORIES = [
    "payroll",
    "card payment",
    "deposit",
]

DELETE_COL_CONFIG = {"_delete": st.column_config.CheckboxColumn("🗑️", default=False)}

EXPENDITURE_COLUMN_CONFIG = {
    "category": st.column_config.SelectboxColumn("Category", options=[""] + EXPENDITURE_CATEGORIES),
    "subcategory": st.column_config.SelectboxColumn("Subcategory", options=[""] + ALL_SUBCATEGORIES),
    "merchant": st.column_config.SelectboxColumn("Merchant", options=[""] + MERCHANTS),
    "ignore": st.column_config.SelectboxColumn("Ignore", options=["False", "True"]),
    "necessity": st.column_config.SelectboxColumn("Necessity", options=[""] + NECESSITY),
    **DELETE_COL_CONFIG,
}

DEPOSIT_COLUMN_CONFIG = {
    "category": st.column_config.SelectboxColumn("Category", options=[""] + DEPOSIT_CATEGORIES),
    **DELETE_COL_CONFIG,
}

DISABLED_COLS = ["date", "description", "amount", "account"]


def load_expenditures(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, index_col=0)
    df["ignore"] = df["ignore"].astype(str)
    for col in ["category", "subcategory", "merchant", "necessity"]:
        df[col] = df[col].fillna("").astype(str)
    df["_delete"] = False
    return df[["date", "description", "amount", "account",
               "category", "subcategory", "necessity", "merchant", "ignore", "_delete"]]


def load_deposits(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, index_col=0)
    df["category"] = df["category"].fillna("").astype(str)
    df["_delete"] = False
    return df


st.set_page_config(page_title="Budget Transactions", layout="wide")

if "view" not in st.session_state:
    st.session_state.view = "Expenditures"

st.sidebar.markdown("**Transactions**")
for _opt in ["Expenditures", "Deposits"]:
    if st.sidebar.button(
        _opt, key=f"nav_{_opt}", use_container_width=True,
        type="primary" if st.session_state.view == _opt else "secondary"
    ):
        st.session_state.view = _opt
        st.rerun()

st.sidebar.markdown("**Single Period**")
if st.sidebar.button(
    "Pie Chart", key="nav_pie", use_container_width=True,
    type="primary" if st.session_state.view == "Pie Chart" else "secondary"
):
    st.session_state.view = "Pie Chart"
    st.rerun()

view = st.session_state.view

# ── Pie Chart view ────────────────────────────────────────────────────────────
if view == "Pie Chart":
    st.title("Pie Chart")

    today = date.today()
    first_of_month = today.replace(day=1)

    ctrl1, ctrl2, ctrl3 = st.columns([1, 1, 1])
    with ctrl1:
        start_date = st.date_input("Start date", value=first_of_month)
    with ctrl2:
        end_date = st.date_input("End date", value=today)
    with ctrl3:
        data_type = st.radio("Show", ["Expenditures", "Deposits"], horizontal=True)

    if data_type == "Expenditures":
        raw = load_expenditures(EXPENDITURES_PATH)
        raw = raw[raw["ignore"].str.lower() != "true"]
    else:
        raw = load_deposits(DEPOSITS_PATH)

    raw["date"] = pd.to_datetime(raw["date"])
    filtered = raw[
        (raw["date"].dt.date >= start_date) &
        (raw["date"].dt.date <= end_date)
    ].copy()

    if filtered.empty:
        st.info("No transactions found for the selected period.")
    else:
        filtered["amount"] = filtered["amount"].abs()

        # Category pie chart
        cat_totals = (
            filtered[filtered["category"] != ""]
            .groupby("category", as_index=False)["amount"]
            .sum()
        )

        if cat_totals.empty:
            st.warning("No categorised transactions in this period.")
        else:
            fig_cat = px.pie(
                cat_totals, values="amount", names="category",
                title=f"{data_type} by Category"
            )
            fig_cat.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_cat, use_container_width=True)

        # Subcategory breakdown (expenditures only)
        if data_type == "Expenditures":
            st.markdown("---")
            st.subheader("Category Breakdown by Subcategory")

            cats_with_sub = sorted(
                filtered[
                    (filtered["subcategory"] != "") &
                    (filtered["category"] != "")
                ]["category"].unique().tolist()
            )

            if not cats_with_sub:
                st.info("No subcategory data available for this period.")
            else:
                selected_cat = st.selectbox("Select category", cats_with_sub)
                sub_totals = (
                    filtered[
                        (filtered["category"] == selected_cat) &
                        (filtered["subcategory"] != "")
                    ]
                    .groupby("subcategory", as_index=False)["amount"]
                    .sum()
                )

                if sub_totals.empty:
                    st.info(f"No subcategory breakdown available for '{selected_cat}'.")
                else:
                    fig_sub = px.pie(
                        sub_totals, values="amount", names="subcategory",
                        title=f"{selected_cat} — Subcategory Breakdown"
                    )
                    fig_sub.update_traces(textposition="inside", textinfo="percent+label")
                    st.plotly_chart(fig_sub, use_container_width=True)

# ── Transactions table view ───────────────────────────────────────────────────
else:
    tab = view
    if tab == "Expenditures":
        st.title("Expenditures")
        path = EXPENDITURES_PATH
        key = "exp_df"
    else:
        st.title("Deposits")
        path = DEPOSITS_PATH
        key = "dep_df"

    if key not in st.session_state:
        if tab == "Expenditures":
            st.session_state[key] = load_expenditures(path)
        else:
            st.session_state[key] = load_deposits(path)

    column_config = EXPENDITURE_COLUMN_CONFIG if tab == "Expenditures" else DEPOSIT_COLUMN_CONFIG

    edited = st.data_editor(
        st.session_state[key],
        key=f"{key}_editor",
        use_container_width=True,
        num_rows="fixed",
        column_config=column_config,
        disabled=DISABLED_COLS,
    )

    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("Delete Selected"):
            kept = edited[~edited["_delete"]].copy()
            kept["_delete"] = False
            kept.drop(columns=["_delete"]).to_csv(path)
            st.session_state[key] = kept
            del st.session_state[f"{key}_editor"]
            st.rerun()
    with col2:
        if st.button("Save to CSV"):
            st.session_state[key] = edited
            edited.drop(columns=["_delete"]).to_csv(path)
            st.success("Saved.")
