import streamlit as st
import pandas as pd
import itertools
import collections
import time

st.title("🎯 Lottery Deep Search — 4 Digit (0-9) Engine")

st.write("""
Upload an Excel file with two columns:  
**Column A = Ticket (comma-separated digits)**  
**Column B = Category (Straight / Rumble / Chance)**  
Example ticket: `1,2,3,4`
""")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None).iloc[1:]
    df = df[[0,1]].rename(columns={0:'ticket',1:'category'})
    df['ticket'] = df['ticket'].astype(str).str.strip()

    tickets = []
    cats = df['category'].tolist()

    for s in df['ticket'].tolist():
        parts = [int(x) for x in s.split(',')]
        tickets.append(parts)

    straight_counts = collections.Counter()
    rumble_counts = collections.Counter()
    chance_counts = collections.Counter()

    for t,c in zip(tickets,cats):
        tup = tuple(t)
        if c=='Straight':
            straight_counts[tup] += 1
        elif c=='Rumble':
            rumble_counts[tuple(sorted(t))] += 1
        else:
            chance_counts[tup] += 1

    rumble_patterns = [(collections.Counter(k), cnt) for k,cnt in rumble_counts.items()]

    chance_suffix_counts = {1:collections.Counter(), 2:collections.Counter(),
                            3:collections.Counter(), 4:collections.Counter()}

    for t,cnt in chance_counts.items():
        for L in range(1,5):
            chance_suffix_counts[L][tuple(t[-L:])] += cnt

    chance_payout_map = {1:15,2:100,3:1100,4:7500}

    def evaluate_draw(draw):
        draw_tuple = tuple(draw)
        total = 0

        total += straight_counts.get(draw_tuple, 0) * 18500

        draw_cnt = collections.Counter(draw)
        for tcnt, cnt in rumble_patterns:
            md = sum(min(draw_cnt.get(d,0), tcnt.get(d,0)) for d in draw_cnt)
            if md == 4:
                total += 1750 * cnt
            elif md == 3:
                total += 250 * cnt

        c4 = chance_suffix_counts[4].get(draw_tuple, 0)
        total += c4 * chance_payout_map[4]

        s3 = tuple(draw[-3:])
        c3 = chance_suffix_counts[3].get(s3, 0) - c4
        if c3 > 0:
            total += c3 * chance_payout_map[3]

        s2 = tuple(draw[-2:])
        c2 = chance_suffix_counts[2].get(s2, 0) - chance_suffix_count
