import os
import requests

BOARD_ID = "zNSAT4U"

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
TRELLO_KEY = os.getenv("TRELLO_KEY")

if not DISCORD_WEBHOOK:
    raise Exception("DISCORD_WEBHOOK secret missing!")

if not TRELLO_KEY:
    raise Exception("TRELLO_KEY secret missing!")

STATE_FILE = "last_action.txt"

url = f"https://api.trello.com/1/boards/{BOARD_ID}/actions?limit=5&key={TRELLO_KEY}"

print("Checking Trello...")
response = requests.get(url, timeout=20)

print("Status:", response.status_code)
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

print("Latest ID:", latest_id)
print("Previous ID:", last_id)

if latest_id != last_id and last_id != "":
    card = latest.get("data", {}).get("card", {}).get("name", "Unknown card")
    action_type = latest.get("type", "update")
    member = latest.get("memberCreator", {}).get("fullName", "Someone")
    short_link = latest.get("data", {}).get("card", {}).get("shortLink", "")

    link = f"https://trello.com/c/{short_link}" if short_link else f"https://trello.com/b/{BOARD_ID}"

    payload = {
        "content": f"🚗 **Trello Update Detected**\n\n**Card:** {card}\n**Action:** {action_type}\n**By:** {member}\n\n{link}"
    }

    discord_response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=20)
    print("Discord response:", discord_response.status_code)
else:
    print("No new update detected, or first run setup.")

with open(STATE_FILE, "w") as f:
    f.write(latest_id)

print("Done.")
