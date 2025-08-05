from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import os
import re
from query_bot import answer_query

# Load environment variables
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
    print("Error: Missing Slack tokens in environment variables!")
    exit(1)

# Initialize Slack app
app = App(token=SLACK_BOT_TOKEN)

# Get bot's user ID
try:
    BOT_ID = app.client.auth_test()["user_id"]
    print(f"Bot ID: {BOT_ID}")
except Exception as e:
    print(f"Error getting bot ID: {e}")
    exit(1)

# Compile regex for mention detection
MENTION_RE = re.compile(rf"<@{BOT_ID}>\s*(.+)", re.DOTALL)

@app.event("message")
def handle_message_events(body, say, logger):
    event = body.get("event", {})
    text = event.get("text", "")
    user = event.get("user")

    logger.info(f"Received message: {text}")

    # Ignore messages from bots, threads, or no user
    if not user or event.get("subtype") or user == BOT_ID:
        return

    # Check if bot is mentioned
    m = MENTION_RE.match(text)
    if not m:
        return

    user_query = m.group(1).strip()
    logger.info(f"Processing query: {user_query}")

    try:
        response = answer_query(user_query)
        say(response)
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        say("Sorry, I encountered an error. Please try again.")

@app.event("app_mention")
def handle_app_mentions(body, say, logger):
    """Handle direct mentions"""
    event = body.get("event", {})
    text = event.get("text", "")
    
    # Remove the mention from the text
    clean_text = re.sub(rf"<@{BOT_ID}>\s*", "", text).strip()
    
    if not clean_text:
        say("Hello! How can I help you today?")
        return
    
    try:
        response = answer_query(clean_text)
        say(response)
    except Exception as e:
        logger.error(f"Error: {e}")
        say("Sorry, I'm having trouble right now. Please try again later.")

if __name__ == "__main__":
    print("Starting BIT-Ninja bot...")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
