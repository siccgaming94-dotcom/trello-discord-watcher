import os
import requests

BOARD_ID = "zNSAT4U"
DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]
STATE_FILE = "last_action.txt"

url = f"https://api.trello.com/1/boards/{BOARD_ID}/actions?limit=5"

response = requests.get(url, timeout=20)
response.raise_for_status()
actions = response.json()

if not actions:
    print("No actions found.")
    exit()

latest = actions[0]
latest_id = latest["id"]

last_id = ""
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        last_id = f.read().strip()

if latest_id != last_id and last_id != "":
    card = latest.get("data", {}).get("card", {}).get("name", "Unknown card")
    action_type = latest.get("type", "update")
    member = latest.get("memberCreator", {}).get("fullName", "Someone")
    date = latest.get("date", "")
    short_link = latest.get("data", {}).get("card", {}).get("shortLink", "")

    if short_link:
        link = f"https://trello.com/c/{short_link}"
    else:
        link = f"https://trello.com/b/{BOARD_ID}"

    message = {
        "content": f"🚗 **Trello Update Detected**\n\n**Card:** {card}\n**Action:** {action_type}\n**By:** {member}\n**Time:** {date}\n\n{link}"
    }

    requests.post(DISCORD_WEBHOOK, json=message, timeout=20)
    print("Sent Discord notification.")
else:
    print("No new update, or first run setup.")

with open(STATE_FILE, "w") as f:
    f.write(latest_id)
