"""
Handle interactions with slack interactive elements
"""
import json
import logging
import requests
from slack_sdk import WebClient
from slack_handlers.slack_events_handler import SlackEventsHandler
from utils.dynamo import DynamoUtils


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def interaction_handler(message, _context):
    """
    Handles interactive events from Slack elements like buttons
    """
    response_url = message.get("response_url")
    interaction_type = message.get("type")
    team = message.get("team")
    team_id = team.get("id")
    slack_access_token = DynamoUtils.get_slack_access_token(team_id)
    client = WebClient(token=slack_access_token)
    if interaction_type == "view_submission":
        view = message.get("view")
        block_id = view.get("blocks")[0].get("block_id")
        action_id = view.get("blocks")[0].get("element").get("action_id")
        if action_id == "incident_resolution":
            incident_id = ""
            try:
                resolution_text = (
                    view.get("state")
                    .get("values")
                    .get(block_id)
                    .get("incident_resolution")
                    .get("value")
                )
                incident_id = view.get("private_metadata")
                slack_events_handler = SlackEventsHandler(client, team_id)
                slack_events_handler.close_incident_and_add_resolution(
                    incident_id, resolution_text
                )
                return "ok"
            except Exception as ex:
                logger.error(
                    f"error closing incident for team {team_id} and incident {incident_id} {ex}"
                )
                client.chat_postMessage(
                    channel=incident_id,
                    text="There was an error closing the incident. Please contact support",
                )
                return "failed"

    else:
        action = message.get("actions")[0]
        action_id = action.get("action_id")
        if action_id == "cancel":
            __update_original_message(response_url, "Incident creation cancelled")
        elif action_id == "create_incident":
            if "team" in message and "id" in message.get("team"):
                try:
                    container = message.get("container")
                    channel = container.get("channel_id")
                    incident_name = action.get("value")
                    slack_events_handler = SlackEventsHandler(client, team_id)
                    slack_events_handler.create_new_incident(channel, incident_name)
                    __delete_original_message(response_url)
                except Exception as e:
                    logger.error(f"exception during incident creation {e}")
                    return "error"
    return "ok"


def __update_original_message(response_url, message):
    response_payload = {"replace_original": "true", "text": message}
    headers = {"Content-Type": "application/json"}
    requests.post(response_url, headers=headers, data=json.dumps(response_payload))


def __delete_original_message(response_url):
    response_payload = {"delete_original": "true"}
    headers = {"Content-Type": "application/json"}
    requests.post(response_url, headers=headers, data=json.dumps(response_payload))
