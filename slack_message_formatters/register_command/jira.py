import os
import urllib
from slack_message_formatters.register_command.integrated_service import (
    IntegratedServiceFormatter,
)


class Jira(IntegratedServiceFormatter):

    JIRA_OAUTH_ACCESS_CODE_URL = "https://auth.atlassian.com/authorize/"
    JIRA_OAUTH_ACCESS_TOKEN_URL = "https://auth.atlassian.com/oauth/token"
    JIRA_CLIENT_ID = os.environ["JIRA_CLIENT_ID"]
    JIRA_REDIRECT_URL = os.environ["JIRA_REDIRECT_URL"]

    def build_oauth_entry(self, teamId, userId, authorized_apps):
        jira = []
        jira_section = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "* 1️⃣ Jira*"},
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Register",
                },
                "url": self.build_access_code_link(teamId, userId),
                "value": "jira",
            },
        }

        jira.append(jira_section)

        if "jira" in authorized_apps:
            jira_registered = super().build_already_registered_item()
            jira.append(jira_registered)

        return jira

    def build_access_code_link(self, teamId, userId):
        state_param = super().build_state_param(teamId, userId)
        redirect_url = urllib.parse.quote(self.JIRA_REDIRECT_URL, safe="")
        url = f"{self.JIRA_OAUTH_ACCESS_CODE_URL}?audience=api.atlassian.com&client_id={self.JIRA_CLIENT_ID}&scope=read%3Ajira-user%20write%3Ajira-work%20offline_access&redirect_uri={redirect_url}&state={state_param}&response_type=code&prompt=consent"
        return url
