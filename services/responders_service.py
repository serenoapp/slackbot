"""
Service that will deal with responders
"""
from typing import List
from utils.dynamo import DynamoUtils
from domain.responders_list import RespondersList
from domain.slack_responder import SlackResponder


class RespondersService:
    """
    Class that handles responders
    """

    def __init__(self, team_id):
        self.team_id = team_id

    def get_oncall(self, team_id):
        """Gets current oncall"""
        return DynamoUtils.get_oncall(team_id)

    def get_responders(self):
        """Returns the list of responders that have been set"""
        return RespondersList.list(self.team_id)

    def get_responders_with_oncall(
        self,
    ) -> List[SlackResponder]:  # TODO - use interface instead of SlackResponder
        """
        Returns a list that is a combination of responders and oncall.
        An oncall is treated a responder
        """
        responders: List[SlackResponder] = RespondersList.list(self.team_id)
        oncall = DynamoUtils.get_oncall(self.team_id)
        oncall_responder: SlackResponder = SlackResponder(oncall)

        if oncall_responder.id is not None and not any(
            responder.id == oncall_responder.id for responder in responders
        ):
            responders.append(oncall_responder)
        return responders

    def set_oncall(self, user_id):
        """Sets the oncall in the database"""
        return DynamoUtils.save_oncall(self.team_id, user_id)

    def set_responders(self, responders_list: List[str]):
        """Sets a list of responders in the database"""
        return RespondersList.add(self.team_id, responders_list)

    def remove_responders(self, responders_list: List[str]):
        """Removes a list of responders from the database"""
        return RespondersList.remove(self.team_id, responders_list)
