from abc import ABC, abstractmethod
import base64

"""
Abstract class that represents a generic message formatter for the "/sereno register" slack command.
Each new service that is added to the slackbot integration has to extend this class and implement the abstract methods
RegisterCommandFormatter will have a list of IntegratedService(s) classes and will build the slackbot response with the respective oauth links for each service
"""


class IntegratedServiceFormatter(ABC):
    @abstractmethod
    def build_oauth_entry(self, team_id, user_id, authorized_apps):
        pass

    @abstractmethod
    def build_access_code_link(self, team_id, user_id):
        pass

    def build_already_registered_item(self):
        return {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": ":white_check_mark:"},
                {"type": "plain_text", "emoji": True, "text": "Already registered"},
            ],
        }

    def build_state_param(self, teamId, userId):
        data = teamId + ":" + userId
        encoded_bytes = base64.b64encode(data.encode("utf-8"))
        encoded_str = str(encoded_bytes, "utf-8")
        return encoded_str
