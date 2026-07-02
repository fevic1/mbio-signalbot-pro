#!/usr/bin/env python3
import yaml
from langsmith import Client
from datetime import datetime, timedelta

CONFIG_PATH = "/app/config/strategy_config.yaml"

def get_average_score(hours_back=72):
    client = Client()
    cutoff = datetime.now() - timedelta(hours=hours_back)
    feedbacks = client.list_feedback(
        key="trade_quality",
        min_created_at=cutoff,
        limit=100
    )
    scores = [fb.score for fb in feedbacks if fb.score is not None]
    if not scores:
        return None
    return sum(scores) / len(scores)

def update_risk_config(avg_score):
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    current = config["risk"]["max_risk_per_trade_pct"]
    if avg_score > 7:
        new_risk = min(current + 0.005, 0.04)
    elif avg_score < 5:
        new_risk = max(current - 0.005, 0.005)
    else:
        new_risk = current
    if new_risk != current:
        config["risk"]["max_risk_per_trade_pct"] = new_risk
        with open(CONFIG_PATH, "w") as f:
            yaml.safe_dump(config, f)
        print(f"Risk updated: {current} -> {new_risk}")
    else:
        print(f"Risk unchanged: {current}")

if __name__ == "__main__":
    avg = get_average_score()
    if avg is not None:
        update_risk_config(avg)
    else:
        print("No trade quality scores yet.")
