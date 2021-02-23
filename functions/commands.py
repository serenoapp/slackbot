"""
Handle slack slash commands
"""
import re
from slack_sdk import WebClient
from slack_handlers.slack_commands_handler import SlackCommandsHandler
from slack_message_formatters.help_formatter import HelpFormatter
from utils.dynamo import DynamoUtils


# responders_regex = "\<@([^\|]+)\|([^\>]+)\>" # in case we want to extract both username and user id

USER_ID_REGEX = "\<@([^\|]+)"
CHANNEL_ID_REGEX = "\<#([^\|]+)"


def command_handler(message, _context):
    """
    Handles commands sent to slackbot
    """
    team_id = message["team_id"]
    user_id = message["user_id"]
    command = message["text"]
    trigger_id = message.get("trigger_id")
    channel_id = message.get("channel_id")
    slack_access_token = DynamoUtils.get_slack_access_token(team_id)
    client = WebClient(token=slack_access_token)
    slack_commands_handler = SlackCommandsHandler(team_id)
    if "register" in command:
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            blocks=slack_commands_handler.build_register_response(user_id).get(
                "blocks"
            ),
        )
    elif "responders" in command:
        if "add" in command:
            responders_list_users = re.findall(USER_ID_REGEX, command)
            responders_list_channels = re.findall(CHANNEL_ID_REGEX, command)
            responders_list = responders_list_users + responders_list_channels
            if len(responders_list) == 0:
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text="List of responders cannot be empty!",
                )
            response = slack_commands_handler.add_responders(responders_list)
            client.chat_postEphemeral(channel=channel_id, user=user_id, text=response)
        elif "remove" in command:
            responders_list_users = re.findall(USER_ID_REGEX, command)
            responders_list_channels = re.findall(CHANNEL_ID_REGEX, command)
            responders_list = responders_list_users + responders_list_channels
            response = slack_commands_handler.remove_responders(responders_list)
            client.chat_postEphemeral(channel=channel_id, user=user_id, text=response)
        elif "list" in command:
            response = slack_commands_handler.list_responders()
            client.chat_postEphemeral(channel=channel_id, user=user_id, text=response)
        else:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Sorry I did not understand the command: options are add, remove, list",
            )
    elif "oncall" in command:
        if "set" in command:
            user_matched = re.search(USER_ID_REGEX, command)
            if user_matched is not None:
                user_id_to_set = user_matched.group(1)
                slack_commands_handler.set_oncall(user_id_to_set)
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text="<@%s> set as oncall" % user_id_to_set,
                )
            else:
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text="Sorry, wrong format. Do `/sereno set oncall <user>`",
                )
    elif "help" in command:
        formatter = HelpFormatter()
        client.chat_postEphemeral(
            channel=channel_id, user=user_id, blocks=formatter.format().get("blocks")
        )
    elif "close incident" in command:
        slack_commands_handler.show_close_incident_modal(
            team_id, channel_id, trigger_id
        )
    else:
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="Sorry I did not understand the command. "
            "Type `/sereno help` to see a list of available commands",
        )
