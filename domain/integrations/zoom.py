from domain.token_data import TokenData
from domain.integrations.integration import Integration
from flask import url_for
from utils.integration_enum import IntegrationType


class Zoom(Integration):
    def __init__(self, token_data: TokenData):
        self.token_data = token_data
        self.link = ""
        # self.logo = "https://905d09d9d54f.ngrok.io" + url_for('static', filename='img/zoom_logo.png')

    def is_valid(self) -> bool:
        return self.token_data.is_valid()

    def get_token_data(self) -> TokenData:
        return self.token_data

    def get_logo(self):
        # return self.logo
        return ""

    def get_link(self):
        return self.link

    def get_code(self):
        """
        Returns the identifier. For a call should be the call id, for a ticket a ticket id, etc
        """
        pass

    def get_type(self):
        return IntegrationType.CALL
