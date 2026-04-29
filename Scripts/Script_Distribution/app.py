import streamlit as st
import pandas as pd

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Script Niche Dashboard", layout="wide")

st.title("🎯 Script → Influencer Niche Mapping")

# ---------- LOAD DATA ----------
df = pd.read_csv(r"Scripts//Script_Distribution//script_distribution.csv")

# ---------- KEEP ONLY REQUIRED COLUMNS ----------
df = df[[
    "Script Name",
    "Primary Niche",
    "Secondary Niche",
    "Tertiary Niche"
]]

# ---------- RESET INDEX FROM 1 ----------
df.index = range(1, len(df) + 1)

# ---------- SIDEBAR FILTER ----------
st.sidebar.header("Filter by Niche")

all_niches = pd.concat([
    df["Primary Niche"],
    df["Secondary Niche"],
    df["Tertiary Niche"]
]).unique()

selected_niches = st.sidebar.multiselect(
    "Select Niche",
    options=all_niches,
    default=all_niches
)

# ---------- FILTER LOGIC ----------
filtered_df = df[
    (df["Primary Niche"].isin(selected_niches)) |
    (df["Secondary Niche"].isin(selected_niches)) |
    (df["Tertiary Niche"].isin(selected_niches))
]

# ---------- TABLE ----------
st.subheader("📋 Script Niche Table")
st.dataframe(filtered_df, use_container_width=True)

# ---------- COUNT ----------
st.metric("Total Scripts Showing", len(filtered_df))

# ---------- SEARCH ----------
st.subheader("🔍 Search Script")

search = st.text_input("Search by Script Name")

if search:
    result = df[df["Script Name"].str.contains(search, case=False)]
    st.dataframe(result)

# ---------- QUICK VIEW (IMPORTANT FOR YOU) ----------
st.subheader("🔥 Quick Niche Breakdown")

niche_count = pd.concat([
    df["Primary Niche"],
    df["Secondary Niche"],
    df["Tertiary Niche"]
]).value_counts()

st.dataframe(niche_count.head(15))