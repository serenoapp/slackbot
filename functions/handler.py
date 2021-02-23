"""
Lambda function to handle slackbot interaction
"""

import re
import os
import base64
import json
import logging
from slackeventsapi import SlackEventAdapter
from flask import Flask, redirect, render_template, request
from domain.integrations.jira import Jira
from domain.integrations.zoom import Zoom
from domain.token_data import TokenData
from utils.aws import AwsUtils
from utils.dynamo import DynamoUtils
from services.oauth_services.slack_oauth_service import SlackOauthService
from services.oauth_services.jira_oauth_service import JiraOauthService
from services.oauth_services.zoom_oauth_service import ZoomOauthService

from functions.invoke import invoke_lambda

app = Flask(__name__)

SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
STAGE = os.environ["STAGE"]
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)

USERS_TABLE = os.environ["USERS_TABLE"]
dynamoResource = AwsUtils.get_dynamodb_resource()

USER_ID_REGEX = "\<@([^\|]+)>"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@app.route("/")
def is_alive():
    """Test endpoint"""
    return "Im up!"


@app.route("/signin")
def signin():
    """Test endpoint"""
    return render_template("index.html")


@app.route("/jira/auth")
def jira_oauth():
    """Endpoint to jira oauth flow"""
    code = request.args.get("code") or "no code!"
    state = request.args.get("state")
    decoded_state = base64.b64decode(state).decode()
    team_id, user_id = decoded_state.split(":")
    token_data: TokenData = JiraOauthService.get_token_data(code)
    try:
        account_id = JiraOauthService.get_jira_id(token_data.access_token)
        jira = Jira(token_data, account_id)
        DynamoUtils.save_jira_data(team_id, jira)
        return redirect(
            f"https://slack.com/app_redirect?app=A01H45TA509&team={team_id}", code=302
        )
    except Exception as e:
        logger.error(
            f"Could not authenticate jira app for team: {team_id} and user: {user_id} - {e}"
        )
        return ""


@app.route("/slack/auth")
def slack_auth():
    """Endpoint to slack oauth flow"""
    code = request.args.get("code") or "no code!"
    try:
        team_id, access_token = SlackOauthService.get_access_token(code)
        DynamoUtils.save_slack_access_token(team_id, access_token)
        return redirect(
            f"https://slack.com/app_redirect?app=A01H45TA509&team={team_id}", code=302
        )
    except Exception as e:
        logger.error(f"ERROR: slack/oauth {e}")


@app.route("/zoom/auth")
def zoom_auth():
    """Endpoint to zoom oauth flow"""
    code = request.args.get("code") or "no code!"
    state = request.args.get("state")
    decoded_state = base64.b64decode(state).decode()
    team_id, _user_id = decoded_state.split(":")
    token_data: TokenData = ZoomOauthService.get_token_data(code)
    zoom = Zoom(token_data)
    DynamoUtils.save_zoom_data(team_id, zoom)
    return redirect(
        f"https://slack.com/app_redirect?app=A01H45TA509&team={team_id}", code=302
    )


@app.route("/slack/command/", methods=["POST"])
def commands():
    """
    Receives commands from slackbot
    """
    logger.info("got command, dispatching to lambda...")
    message = request.form
    payload = json.dumps(message).encode("utf-8")
    invoke_lambda(f"slackbot-{STAGE}-command", "Event", payload)
    return ""


@app.route("/interactive", methods=["POST"])
def interactive():
    """
    Handles interactive events from Slack elements like buttons
    """
    logger.info("Interaction received, dispatching to lambda...")
    message = request.form
    json_payload = json.loads(message.get("payload"))
    payload = json.dumps(json_payload).encode("utf-8")
    invoke_lambda(f"slackbot-{STAGE}-interactive", "Event", payload)
    return ""


@slack_events_adapter.on("message")
def handle_message(event_data):
    """
    Handles messages from slack
    """
    logger.info("Message received, dispatching to lambda...")
    payload = json.dumps(event_data["event"]).encode("utf-8")
    invoke_lambda(f"slackbot-{STAGE}-message", "Event", payload)
    return True


@slack_events_adapter.on("app_mention")
def handle_mention(event_data):
    """
    Handles slackbot's mentions
    """
    logger.info("Mention received, dispatching to lambda...")
    payload = json.dumps(event_data["event"]).encode("utf-8")
    invoke_lambda(f"slackbot-{STAGE}-mention", "Event", payload)
    return True


def sanitise_incident_name(name):
    """Remove unnecessary characters from incident name"""
    # remove bot id
    name = re.sub(USER_ID_REGEX, "", name)
    # remove command
    name = name.replace("new incident", "").replace("create incident", "").strip()
    return name


# Error events
@slack_events_adapter.on("error")
def error_handler(err):
    """Handle slack errors"""
    logger.error("ERROR: " + str(err))


# Start the flask server on port 3000
if __name__ == "__main__":
    app.run(port=3000)
