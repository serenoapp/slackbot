from typing import List
from slack_message_formatters.register_command.integrated_service import (
    IntegratedServiceFormatter,
)
from utils.dynamo import DynamoUtils

"""
Class whose responsibility is to build and format the response to slackbot command /register_command
"""


class RegisterCommandFormatter:
    services: List[IntegratedServiceFormatter] = []

    def __init__(self, services: List[IntegratedServiceFormatter]):
        self.services = services

    def format(self, team_id, user_id):
        services_section = []
        authorized_apps = DynamoUtils.get_authorized_apps(team_id)
        for service in self.services:
            services_section.append(
                service.build_oauth_entry(team_id, user_id, authorized_apps)
            )
        response = self.__build_response(services_section)
        return self.__build_response(services_section)

    def __build_response(self, services):
        response = {
            # "response_type": "in_channel",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Hey there 👋 I'm Sereno. I'm here to help you configure the different services I need to work properly.\nYou will have to authorize the following apps to be used by me.",
                    },
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": ":bulb: I recommend you create a user in each service to be used specifically for this",
                        }
                    ],
                },
                {"type": "divider"},
            ]
        }

        for service in services:
            response["blocks"].extend(service)
            response["blocks"].append({"type": "divider"})

        return response
