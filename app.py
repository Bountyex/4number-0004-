import streamlit as st
import pandas as pd
from itertools import product
from collections import Counter

st.set_page_config(page_title="Lottery Optimizer", layout="wide")

st.title("🎯 4-Digit Lottery - Absolute Lowest Payout Finder")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    # -----------------------------
    # Load & Clean Data
    # -----------------------------
    df = pd.read_excel(uploaded_file)

    st.write("Original Columns:", df.columns.tolist())
    st.write("Original Shape:", df.shape)

    # Keep first 2 columns only
    df = df.iloc[:, :2]
    df.columns = ["Ticket", "Category"]
    df = df.dropna()

    def parse_ticket(t):
        return [int(x.strip()) for x in str(t).split(",")]

    df["Digits"] = df["Ticket"].apply(parse_ticket)

    st.success("File processed successfully!")

    # -----------------------------
    # Force Global Minimum Button
    # -----------------------------
    if st.button("🚀 Force Absolute Lowest Result"):

        # Pre-group tickets (faster)
        straight_tickets = []
        chance_tickets = []
        rumble_counters = []

        for _, row in df.iterrows():
            digits = row["Digits"]
            category = str(row["Category"]).strip().lower()

            if category == "straight":
                straight_tickets.append(digits)
            elif category == "chance":
                chance_tickets.append(digits)
            elif category == "rumble":
                rumble_counters.append(Counter(digits))

        best_combo = None
        lowest_payout = float("inf")

        progress_bar = st.progress(0)
        total_combos = 10000
        checked = 0

        # -----------------------------
        # Search All 0000–9999
        # -----------------------------
        for combo in product(range(10), repeat=4):

            total_payout = 0

            # 1️⃣ STRAIGHT (Highest risk first - 18500)
            for ticket in straight_tickets:
                match = 0
                for i in range(4):
                    if combo[i] == ticket[i]:
                        match += 1
                    else:
                        break

                if match == 4:
                    total_payout += 18500
                    break  # Immediate prune

            if total_payout >= lowest_payout:
                checked += 1
                continue

            # 2️⃣ CHANCE (Second highest risk - 7500)
            for ticket in chance_tickets:
                match = 0
                for i in range(3, -1, -1):
                    if combo[i] == ticket[i]:
                        match += 1
                    else:
                        break

                if match == 1:
                    total_payout += 15
                elif match == 2:
                    total_payout += 100
                elif match == 3:
                    total_payout += 1100
                elif match == 4:
                    total_payout += 7500

                if total_payout >= lowest_payout:
                    break

            if total_payout >= lowest_payout:
                checked += 1
                continue

            # 3️⃣ RUMBLE
            combo_counter = Counter(combo)

            for rc in rumble_counters:
                matches = sum((combo_counter & rc).values())

                if matches == 3:
                    total_payout += 50
                elif matches == 4:
                    total_payout += 1750

                if total_payout >= lowest_payout:
                    break

            # Update best result
            if total_payout < lowest_payout:
                lowest_payout = total_payout
                best_combo = combo

            checked += 1
            if checked % 200 == 0:
                progress_bar.progress(checked / total_combos)

        progress_bar.progress(1.0)

        # -----------------------------
        # Display Result
        # -----------------------------
        st.success("✅ Absolute Global Minimum Found!")

        st.subheader("🏆 Best Combination")
        st.write("Combination:", ",".join(map(str, best_combo)))
        st.write("Total Payout:", lowest_payout)
