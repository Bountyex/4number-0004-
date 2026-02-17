import streamlit as st
import pandas as pd
from collections import Counter
from itertools import product

st.set_page_config(page_title="Lottery Optimizer", layout="wide")

st.title("🎯 4-Digit Lottery Lowest Payout Optimizer")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

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

    # ---------------- Reward Rules ----------------

    def straight_reward(m):
        return 18500 if m == 4 else 0

    def rumble_reward(m):
        if m == 3:
            return 50
        if m == 4:
            return 1750
        return 0

    def chance_reward(m):
        if m == 1:
            return 15
        if m == 2:
            return 100
        if m == 3:
            return 1100
        if m == 4:
            return 7500
        return 0

    # ---------------- Matching Logic ----------------

    def straight_match(a, b):
        count = 0
        for i in range(4):
            if a[i] == b[i]:
                count += 1
            else:
                break
        return count

    def chance_match(a, b):
        count = 0
        for i in range(3, -1, -1):
            if a[i] == b[i]:
                count += 1
            else:
                break
        return count

    def rumble_match(a, b):
        ca = Counter(a)
        cb = Counter(b)
        return sum((ca & cb).values())

    # ---------------- Run Optimization ----------------

    if st.button("🚀 Run Optimization"):

        best_combo = None
        lowest_payout = float("inf")
        best_straight = 0
        best_rumble = 0
        best_chance = 0

        progress_bar = st.progress(0)
        total_combos = 10000
        checked = 0

        for combo in product(range(10), repeat=4):

            total_payout = 0
            straight_total = 0
            rumble_total = 0
            chance_total = 0

            for _, row in df.iterrows():
                ticket = row["Digits"]
                category = str(row["Category"]).strip().lower()

                if category == "straight":
                    m = straight_match(combo, ticket)
                    reward = straight_reward(m)
                    straight_total += reward

                elif category == "rumble":
                    m = rumble_match(combo, ticket)
                    reward = rumble_reward(m)
                    rumble_total += reward

                elif category == "chance":
                    m = chance_match(combo, ticket)
                    reward = chance_reward(m)
                    chance_total += reward

                else:
                    continue

                total_payout += reward

                # Early pruning
                if total_payout > lowest_payout:
                    break

            if total_payout < lowest_payout:
                lowest_payout = total_payout
                best_combo = combo
                best_straight = straight_total
                best_rumble = rumble_total
                best_chance = chance_total

            checked += 1
            progress_bar.progress(checked / total_combos)

        st.success("Optimization Completed!")

        st.subheader("🏆 Best Combination Found")
        st.write("Combination:", ",".join(map(str, best_combo)))
        st.write("Total Payout:", lowest_payout)
        st.write("Straight Payout:", best_straight)
        st.write("Rumble Payout:", best_rumble)
        st.write("Chance Payout:", best_chance)
