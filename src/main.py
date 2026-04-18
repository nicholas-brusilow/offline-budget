import streamlit as st
import pandas as pd
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent / "all_transactions.csv"

CATEGORIES = [
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
    "dividends"
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
    "services:cleaners"
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

# --- data loading ---

def load_data():
    df = pd.read_csv(CSV_PATH, index_col=0)
    df["ignore"] = df["ignore"].astype(str)
    for col in ["category", "subcategory", "merchant"]:
        df[col] = df[col].fillna("").astype(str)
    return df

# --- app ---

st.set_page_config(page_title="Budget Transactions", layout="wide")
st.title("Budget Transactions")

if "df" not in st.session_state:
    st.session_state.df = load_data()

edited = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    num_rows="fixed",
    column_config={
        "category": st.column_config.SelectboxColumn(
            "Category",
            options=[""] + CATEGORIES,
        ),
        "subcategory": st.column_config.SelectboxColumn(
            "Subcategory",
            options=[""] + ALL_SUBCATEGORIES,
        ),
        "merchant": st.column_config.SelectboxColumn(
            "Merchant",
            options=[""] + MERCHANTS,
        ),
        "ignore": st.column_config.SelectboxColumn(
            "Ignore",
            options=["False", "True"],
        ),
        "necessity": st.column_config.SelectboxColumn(
            "Necessity",
            options=[""] + NECESSITY,
        ),
    },
    disabled=["date", "description", "amount", "account"],
)

if st.button("Save to CSV"):
    edited.to_csv(CSV_PATH)
    st.session_state.df = edited
    st.success("Saved.")
