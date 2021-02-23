from utils.dynamo import DynamoUtils
from typing import List
from domain.slack_responder import SlackResponder

"""
Class that makes operations on the Responders list
"""


class RespondersList:
    @classmethod
    def list(cls, team_id: str) -> List[SlackResponder]:
        """
        Returns the list of responders from the database.
        """
        responder_id_list = list(DynamoUtils.get_responders(team_id))
        responders = cls.__build_responders_list(responder_id_list)
        return responders

    @classmethod
    def add(cls, team_id: str, responders_list: List[str]) -> List[SlackResponder]:
        """
        Adds one or more responders to the responders list in the database.
        Parameters:
                    team_id(str): Team id
                    responders_list (List[str]): List of slack user ids.
        """
        response = DynamoUtils.save_responders(team_id, responders_list)
        if cls.has_responders(response):
            responders_complete = response.get("Attributes").get("responders")
            responders = cls.__build_responders_list(responders_complete)
            return responders
        return []

    @classmethod
    def remove(cls, team_id: str, responders_list: List[str]) -> List[SlackResponder]:
        """
        Removes one or more responders from the responders list in the database.
        Parameters:
                    team_id(str): Team id
                    responders_list (List[str]): List of slack user ids.
        """
        response = DynamoUtils.remove_responders(team_id, responders_list)
        if cls.has_responders(response):
            responders_complete = response.get("Attributes").get("responders")
            responders = cls.__build_responders_list(responders_complete)
            return responders
        return []

    @classmethod
    def has_responders(cls, response: dict) -> bool:
        return (
            response.get("Attributes") is not None
            and response.get("Attributes").get("responders") is not None
        )

    @classmethod
    def __build_responders_list(cls, responder_id_list):
        responders = []
        for responder_id in responder_id_list:
            slack_responder = SlackResponder(responder_id)
            responders.append(slack_responder)
        return responders
