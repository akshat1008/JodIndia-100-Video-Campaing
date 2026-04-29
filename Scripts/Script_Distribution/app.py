import streamlit as st
import pandas as pd

st.set_page_config(page_title="Campaign Dashboard", layout="wide")

st.title("🚀 Influencer Campaign System")

# ---------- FILE PATHS ----------
scripts_path = r"Scripts/Script_Distribution/script_distribution.csv"
influencer_path = r"Influencers/influencers_master.csv"

# ---------- LOAD DATA (FIXED) ----------
scripts_df = pd.read_csv(scripts_path)
inf_df = pd.read_csv(influencer_path).fillna("")

# ---------- FORCE STRING TYPES (CRITICAL FIX) ----------
for col in ["SCRIPT_SUGGESTIONS", "SCRIPT_SELECTED", "APPROVAL_STATUS"]:
    if col not in inf_df.columns:
        inf_df[col] = ""
    inf_df[col] = inf_df[col].astype(str)

# ---------- EXTRACT SCRIPT NUMBERS ----------
scripts_df["Script Number"] = scripts_df["Script Name"].astype(str).str.extract(r'(\d+)')

# ---------- MATCHING FUNCTION ----------
def get_best_scripts(niche):
    matches = []

    for _, row in scripts_df.iterrows():
        score = 0

        if niche == row["Primary Niche"]:
            score += 3
        elif niche == row["Secondary Niche"]:
            score += 2
        elif niche == row["Tertiary Niche"]:
            score += 1

        if score > 0:
            matches.append((row["Script Number"], score))

    matches = sorted(matches, key=lambda x: x[1], reverse=True)

    return ",".join([m[0] for m in matches[:3]])

# ---------- AUTO GENERATE BUTTON ----------
if st.sidebar.button("⚡ Auto Generate Script Suggestions"):
    inf_df["SCRIPT_SUGGESTIONS"] = inf_df["Niche"].apply(get_best_scripts)
    inf_df.to_csv(influencer_path, index=False)
    st.success("✅ Script Suggestions Generated")

# ---------- TABS ----------
tab1, tab2 = st.tabs(["📊 Script Niches", "🤝 Influencer Manager"])

# ==============================
# 📊 SCRIPT TAB
# ==============================
with tab1:

    df = scripts_df[[
        "Script Name",
        "Primary Niche",
        "Secondary Niche",
        "Tertiary Niche"
    ]]

    df.index = range(1, len(df) + 1)

    st.subheader("📋 Script Niche Table")

    all_niches = pd.concat([
        df["Primary Niche"],
        df["Secondary Niche"],
        df["Tertiary Niche"]
    ]).unique()

    selected_niches = st.multiselect(
        "Filter by Niche",
        options=all_niches,
        default=all_niches
    )

    filtered_df = df[
        (df["Primary Niche"].isin(selected_niches)) |
        (df["Secondary Niche"].isin(selected_niches)) |
        (df["Tertiary Niche"].isin(selected_niches))
    ]

    st.dataframe(filtered_df, use_container_width=True)

    st.metric("Total Scripts Showing", len(filtered_df))

    search = st.text_input("Search Script")

    if search:
        result = df[df["Script Name"].str.contains(search, case=False)]
        st.dataframe(result)

# ==============================
# 🤝 INFLUENCER TAB
# ==============================
with tab2:

    st.subheader("👥 Influencer Management")

    # ---------- STATE FILTER ----------
    states = inf_df["STATE"].dropna().unique()

    selected_states = st.multiselect(
        "Filter by State",
        options=states,
        default=states
    )

    filtered_inf = inf_df[inf_df["STATE"].isin(selected_states)]

    # ---------- USED SCRIPTS ----------
    used_scripts = set(
        inf_df["SCRIPT_SELECTED"].astype(str)
    )

    # ---------- DISPLAY ----------
    for index, row in filtered_inf.iterrows():

        st.markdown(f"### {row['NAME']}")

        col1, col2 = st.columns([2, 2])

        with col1:
            st.write(f"📍 City: {row['TOP CITY']}")
            st.write(f"👥 Followers: {row['FOLLOWERS']}")
            st.write(f"📊 Engagement: {row['ENGAGEMENT RATE']}")
            st.write(f"🎯 Niche: {row['Niche']}")

        # ---------- CLEAN SUGGESTIONS ----------
        suggestions = str(row["SCRIPT_SUGGESTIONS"]).replace("nan", "").split(",")
        suggestions = [s.strip() for s in suggestions if s.strip()]

        # ---------- REMOVE USED SCRIPTS ----------
        available_scripts = [
            s for s in suggestions
            if s not in used_scripts or s == str(row["SCRIPT_SELECTED"])
        ]

        with col2:
            st.write("💡 Suggested Scripts:", suggestions)

            if len(suggestions) == 1:
                choice = st.selectbox(
                    f"Select Script {index}",
                    ["Yes", "No"],
                    key=f"single_{index}"
                )

                if choice == "Yes":
                    inf_df.loc[index, "SCRIPT_SELECTED"] = suggestions[0]
                else:
                    inf_df.loc[index, "SCRIPT_SELECTED"] = ""

            else:
                choice = st.selectbox(
                    f"Choose Script {index}",
                    [""] + available_scripts,
                    key=f"multi_{index}"
                )

                inf_df.loc[index, "SCRIPT_SELECTED"] = choice

        # ---------- APPROVAL ----------
        col3, col4 = st.columns(2)

        with col3:
            if st.button(f"✅ Approve {index}"):
                inf_df.loc[index, "APPROVAL_STATUS"] = "Approved"

        with col4:
            if st.button(f"❌ Reject {index}"):
                inf_df.loc[index, "APPROVAL_STATUS"] = "Rejected"

        st.write("📌 Selected Script:", inf_df.loc[index, "SCRIPT_SELECTED"])
        st.write("📌 Status:", inf_df.loc[index, "APPROVAL_STATUS"])

        st.markdown("---")

    # ---------- SAVE ----------
    if st.button("💾 Save Changes"):
        inf_df.to_csv(influencer_path, index=False)
        st.success("✅ Changes Saved Successfully")

    # ---------- SUMMARY ----------
    st.subheader("📊 Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Influencers", len(inf_df))
    col2.metric("Approved", len(inf_df[inf_df["APPROVAL_STATUS"] == "Approved"]))
    col3.metric("Rejected", len(inf_df[inf_df["APPROVAL_STATUS"] == "Rejected"]))