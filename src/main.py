import streamlit as st
import pandas as pd
from pathlib import Path

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
    "insurance"
]

ALL_SUBCATEGORIES = [
    "transport:public transit",
    "transport:gas",
    "transport:tolls",
    "transport:parking",
    "groceries:staples",
    "groceries:coffee",
    "health and wellness:supplements",
    "health and wellness:gym",
    "utilities:phone",
    "utilities:electric",
    "utilities:internet",
    "utilities:compost",
    "utilities:AI subscription",
    "eating out:coffee",
    "eating out:restaurant",
    "shopping:clothes",
    "shopping:appliances",
    "shopping:tools",
    "services:cleaners",
    "insurance:home",
    "insurance:auto",
    "insurance:health/life"
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
]

DEPOSIT_CATEGORIES = [
    "payroll",
    "card payment",
    "deposit",
]

EXPENDITURE_COLUMN_CONFIG = {
    "category": st.column_config.SelectboxColumn("Category", options=[""] + EXPENDITURE_CATEGORIES),
    "subcategory": st.column_config.SelectboxColumn("Subcategory", options=[""] + ALL_SUBCATEGORIES),
    "merchant": st.column_config.SelectboxColumn("Merchant", options=[""] + MERCHANTS),
    "ignore": st.column_config.SelectboxColumn("Ignore", options=["False", "True"]),
    "necessity": st.column_config.SelectboxColumn("Necessity", options=[""] + NECESSITY),
}

DEPOSIT_COLUMN_CONFIG = {
    "category": st.column_config.SelectboxColumn("Category", options=[""] + DEPOSIT_CATEGORIES),
}

DISABLED_COLS = ["date", "description", "amount", "account"]


def load_expenditures(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, index_col=0)
    df["ignore"] = df["ignore"].astype(str)
    for col in ["category", "subcategory", "merchant", "necessity"]:
        df[col] = df[col].fillna("").astype(str)
    return df


def load_deposits(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, index_col=0)
    df["category"] = df["category"].fillna("").astype(str)
    return df


st.set_page_config(page_title="Budget Transactions", layout="wide")

tab = st.sidebar.radio("View", ["Expenditures", "Deposits"])

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
    use_container_width=True,
    num_rows="fixed",
    column_config=column_config,
    disabled=DISABLED_COLS,
)

st.session_state[key] = edited

if st.button("Save to CSV"):
    edited.to_csv(path)
    st.success("Saved.")
