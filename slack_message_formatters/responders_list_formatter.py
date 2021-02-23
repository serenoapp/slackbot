from typing import List
from domain.slack_responder import SlackResponder

"""
Static class used to format the response from Responders list command
"""


class RespondersListFormatter:
    @staticmethod
    def format(responders: List[SlackResponder], message="Responders: \n") -> str:
        response = message
        cont = 1
        responder: SlackResponder
        for responder in responders:
            if responder.is_user():
                responder_tag = f"<@{responder.id}>"
                response = response + f"{cont}. {responder_tag} \n"
            elif responder.is_channel():
                responder_tag = f"<#{responder.id}>"
                response = response + f"{cont}. {responder_tag} \n"
            cont = cont + 1
        return response
