from slack_sdk import WebClient
from slack_message_formatters.register_command.jira import Jira
from slack_message_formatters.register_command.zoom import Zoom
from slack_message_formatters.close_incident_formatter import CloseIncidentFormatter
from slack_message_formatters.register_command.register_command_formatter import (
    RegisterCommandFormatter,
)
from slack_message_formatters.responders_list_formatter import RespondersListFormatter
from utils.dynamo import DynamoUtils
from services.responders_service import RespondersService


class SlackCommandsHandler:
    """
    Class that handles all slash commands from slackbot
    """

    def __init__(self, team_id):
        self.team_id = team_id
        self.responders_service = RespondersService(team_id)

    def build_register_response(self, user_id):
        """
        Create all the services we currently support (Jira, Zoom, etc)
        Create formatter
        Add services to the formatter list
        Build response
        """
        jira = Jira()
        zoom = Zoom()

        formatter = RegisterCommandFormatter([jira, zoom])
        oauth_response = formatter.format(self.team_id, user_id)
        return oauth_response

    def add_responders(self, responders_list):
        response = self.responders_service.set_responders(responders_list)
        if len(response) == 0:
            return "There was an error adding responders"
        message = "Responders added: \n"
        return RespondersListFormatter.format(response, message)

    def remove_responders(self, responders_list):
        response = self.responders_service.remove_responders(responders_list)
        if len(response) == 0:
            return "Responders removed. List is empty"
        message = "Responders removed. This is the updated list: \n"
        return RespondersListFormatter.format(response, message)

    def list_responders(self):
        response = self.responders_service.get_responders()
        if len(response) == 0:
            return "Responders list is empty"
        return RespondersListFormatter.format(response)

    def set_oncall(self, user_id):
        self.responders_service.set_oncall(user_id)

    def show_close_incident_modal(self, team_id, channel_id, trigger_id):
        """Show a slack modal with an input to add incident resolution text"""
        slack_access_token = DynamoUtils.get_slack_access_token(team_id)
        client = WebClient(token=slack_access_token)
        formatter = CloseIncidentFormatter()
        client.views_open(
            trigger_id=trigger_id, view=formatter.format(channel_id).get("view")
        )
