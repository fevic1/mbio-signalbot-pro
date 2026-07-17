#!/usr/bin/env python3
import os
import sys
from datetime import datetime, timedelta
from langsmith import Client
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

sys.path.append('/app')
from core.memory import collection

client = Client()
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.1-8b-instant")

def get_pnl_for_asset_and_time(asset, trace_time):
    results = collection.get(where={"asset": asset})
    if not results or not results['metadatas']:
        return None
    best_match = None
    min_diff = timedelta(hours=24)
    for meta in results['metadatas']:
        trade_time = datetime.fromisoformat(meta['timestamp'])
        diff = abs(trade_time - trace_time)
        if diff < min_diff:
            min_diff = diff
            best_match = meta
    return best_match['pnl'] if best_match else None

def extract_score(text):
    import re
    match = re.search(r'\b([0-9]|10)\b', text)
    return int(match.group(1)) if match else 5

def evaluate_recent_trades(hours_back=48):
    cutoff = datetime.now() - timedelta(hours=hours_back)
    runs = client.list_runs(project_name="mbio-signalbot", start_time=cutoff, run_type="llm")
    for run in runs:
        asset = run.name
        pnl = get_pnl_for_asset_and_time(asset, run.start_time)
        if pnl is None:
            print(f"No matching trade for {asset}")
            continue
        prompt = f"Score from 1-10 (worst-best): Asset {asset}, Actual PnL: {pnl}%"
        response = llm.invoke([HumanMessage(content=prompt)])
        score = extract_score(response.content)
        client.create_feedback(run.id, key="trade_quality", score=score)
        print(f"{asset}: PnL={pnl}%, Score={score}")

if __name__ == "__main__":
    evaluate_recent_trades(48)
