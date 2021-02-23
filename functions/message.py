import os
import re
from slack_sdk import WebClient
from utils.dynamo import DynamoUtils
from slack_handlers.slack_events_handler import SlackEventsHandler

SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]


def handle_message(msg, _context):
    """
    Handles and reacts to messages sent in slack channels
    """
    team_id = msg.get("team")
    slack_access_token = DynamoUtils.get_slack_access_token(team_id)
    client = WebClient(token=slack_access_token)
    channel = msg["channel"]
    slack_events_handler = SlackEventsHandler(client, team_id)
    if msg.get("subtype") is None and "parca" in msg.get("text"):
        response = "You probably meant Lisandro, <@%s>! :tada:" % msg["user"]
        client.chat_postMessage(channel=channel, text=response)
    elif (
        msg.get("subtype") is None
        and re.search("^log:", msg.get("text"), re.IGNORECASE) is not None
    ):
        text_to_log = msg.get("text").replace("LOG: ", "")
        slack_events_handler.log_comment(channel, text_to_log)
        return
