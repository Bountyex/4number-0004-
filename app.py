import streamlit as st
import pandas as pd
from itertools import product
from collections import Counter
import heapq

st.set_page_config(page_title="Lottery Optimizer", layout="wide")

st.title("🎯 4-Digit Lottery - Lowest & Highest 10 Payout Finder")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    # -----------------------------
    # Load & Clean Data
    # -----------------------------
    df = pd.read_excel(uploaded_file)

    df = df.iloc[:, :2]
    df.columns = ["Ticket", "Category"]
    df = df.dropna()

    def parse_ticket(t):
        return [int(x.strip()) for x in str(t).split(",")]

    df["Digits"] = df["Ticket"].apply(parse_ticket)

    st.success("File processed successfully!")

    if st.button("🚀 Run Full Search (0000–9999)"):

        # -----------------------------
        # Pre-group tickets (FASTER)
        # -----------------------------
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

        # -----------------------------
        # Keep Only Top 10 Lowest & Highest
        # -----------------------------
        lowest_heap = []   # Max heap (store negative)
        highest_heap = []  # Min heap

        progress_bar = st.progress(0)
        total_combos = 10000
        checked = 0

        for combo in product(range(10), repeat=4):

            total_payout = 0

            # Straight
            for ticket in straight_tickets:
                match = 0
                for i in range(4):
                    if combo[i] == ticket[i]:
                        match += 1
                    else:
                        break
                if match == 4:
                    total_payout += 18500

            # Chance
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

            # Rumble
            combo_counter = Counter(combo)
            for rc in rumble_counters:
                matches = sum((combo_counter & rc).values())
                if matches == 3:
                    total_payout += 50
                elif matches == 4:
                    total_payout += 1750

            result = (total_payout, ",".join(map(str, combo)))

            # Maintain Lowest 10
            if len(lowest_heap) < 10:
                heapq.heappush(lowest_heap, (-total_payout, result))
            else:
                if total_payout < -lowest_heap[0][0]:
                    heapq.heappop(lowest_heap)
                    heapq.heappush(lowest_heap, (-total_payout, result))

            # Maintain Highest 10
            if len(highest_heap) < 10:
                heapq.heappush(highest_heap, result)
            else:
                if total_payout > highest_heap[0][0]:
                    heapq.heappop(highest_heap)
                    heapq.heappush(highest_heap, result)

            checked += 1
            if checked % 200 == 0:
                progress_bar.progress(checked / total_combos)

        progress_bar.progress(1.0)

        # -----------------------------
        # Sort Results
        # -----------------------------
        lowest_results = sorted([r[1] for r in lowest_heap], key=lambda x: x[0])
        highest_results = sorted(highest_heap, key=lambda x: -x[0])

        lowest_df = pd.DataFrame(lowest_results, columns=["Total Payout", "Combination"])
        highest_df = pd.DataFrame(highest_results, columns=["Total Payout", "Combination"])

        st.success("✅ Search Completed!")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🟢 Lowest 10 Payouts")
            st.dataframe(lowest_df)

        with col2:
            st.subheader("🔴 Highest 10 Payouts")
            st.dataframe(highest_df)
