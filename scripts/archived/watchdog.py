import os, time, subprocess, requests
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Processes to watch (exact command-line strings)
AGENTS = {
    "AGENT 1💋": "hype_grid.py",
    "AGENT 2🤬": "agent2_btc_market_maker.py",
}

CHECK_INTERVAL = 30         # seconds between checks
REPORT_INTERVAL = 600       # 10 minutes between status reports

def send_telegram(message: str):
    if not TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=5)
    except Exception as e:
        print(f"Telegram send error: {e}")

def is_running(script_name: str) -> bool:
    """Check if a Python process with the given script name is running."""
    try:
        # Use pgrep to search for the exact script name
        result = subprocess.run(["pgrep", "-f", script_name], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def main():
    print("🛡️ Multi‑Agent Watchdog started.")
    send_telegram("🛡️ Multi‑Agent Watchdog started – monitoring AGENT 1💋 and AGENT 2🤬")

    # Track previous state to detect changes
    previous_state = {name: None for name in AGENTS}

    last_report_time = 0

    while True:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        status_lines = []

        for agent_name, script_name in AGENTS.items():
            running = is_running(script_name)
            status_lines.append(f"{agent_name}: {'✅ Online' if running else '❌ Offline'}")

            # Detect change and send immediate alert
            if previous_state[agent_name] is not None and previous_state[agent_name] != running:
                if running:
                    send_telegram(f"✅ {agent_name} is back online. ({timestamp})")
                else:
                    send_telegram(f"🚨 {agent_name} appears OFFLINE! ({timestamp})")

            previous_state[agent_name] = running

        # Periodic full status report every REPORT_INTERVAL seconds
        now = time.time()
        if now - last_report_time >= REPORT_INTERVAL:
            full_report = "📊 *Watchdog Status Report*\n" + "\n".join(status_lines)
            send_telegram(full_report)
            last_report_time = now
            print("\n".join(status_lines))

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
