"""
Handle bots @ mentions
"""
import re
from slack_sdk import WebClient
from utils.dynamo import DynamoUtils
from slack_handlers.slack_events_handler import SlackEventsHandler
from domain.integrations.integration import Integration

USER_ID_REGEX = "\<@([^\|]+)>"


def handle_mention(message, _context):
    """
    Handle bots mentions
    """
    team_id = message.get("team")
    slack_access_token = DynamoUtils.get_slack_access_token(team_id)
    client = WebClient(token=slack_access_token)
    channel = message["channel"]
    slack_events_handler = SlackEventsHandler(client, team_id)
    if message.get("subtype") is None and "alive" in message.get("text"):
        message = "Yes, <@%s>! I am!" % message["user"]
        client.chat_postMessage(channel=channel, text=message)
    elif message.get("subtype") is None and "create ticket" in message.get("text"):
        ticket: Integration = slack_events_handler.create_ticket()
        if ticket is not None:
            client.chat_postMessage(
                channel=channel, text="ticket created: " + ticket.get_link()
            )
        else:
            client.chat_postMessage(
                channel=channel,
                text="Ticket not created. Do you have a ticket integration?",
            )
    elif message.get("subtype") is None and "create call" in message.get("text"):
        call: Integration = slack_events_handler.create_call()
        if call is not None:
            client.chat_postMessage(
                channel=channel, text="call created: " + call.get_link()
            )
        else:
            client.chat_postMessage(
                channel=channel,
                text="Call not created. Do you have a call integration?",
            )
    elif message.get("subtype") is None and "get call" in message.get("text"):
        call_link = slack_events_handler.get_call(channel)
        if bool(call_link):
            client.chat_postMessage(channel=channel, text="Call: " + call_link)
        else:
            client.chat_postMessage(
                channel=channel, text="No call available in this channel"
            )
    elif message.get("subtype") is None and (
        "new incident" in message.get("text")
        or "create incident" in message.get("text")
    ):
        incident_name = sanitise_incident_name(message.get("text"))
        slack_events_handler.handle_new_incident_creation(channel, incident_name)
    elif message.get("subtype") is None and (
        "who is oncall" in message.get("text") or "who’s oncall" in message.get("text")
    ):
        user_id = slack_events_handler.get_oncall(team_id)
        if user_id is None:
            client.chat_postMessage(
                channel=channel,
                text="An oncall hasn't been set yet.```/sereno set oncall <user>```",
            )
            return
        client.chat_postMessage(channel=channel, text=f"<@{user_id}> is oncall")
    elif message.get("subtype") is None and (
        "ongoing" in message.get("text")
        and ("incident" in message.get("text") or "incidents" in message.get("text"))
    ):
        response = slack_events_handler.get_ongoing_incidents_from_today(team_id)
        client.chat_postMessage(channel=channel, blocks=response)


def sanitise_incident_name(name):
    # remove bot id
    name = re.sub(USER_ID_REGEX, "", name)
    # remove command
    name = name.replace("new incident", "").replace("create incident", "").strip()
    return name
