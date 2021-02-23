from domain.token_data import TokenData
from domain.integrations.integration import Integration
from flask import url_for
from utils.integration_enum import IntegrationType


class Jira(Integration):
    def __init__(self, token_data: TokenData, account_id: str):
        self.token_data = token_data
        self.account_id = account_id
        self.link = ""
        # self.logo = "https://905d09d9d54f.ngrok.io" + url_for('static', filename='img/jira_logo.jpg')

    def is_valid(self) -> bool:
        return self.token_data.is_valid() and bool(self.account_id)

    def get_token_data(self) -> TokenData:
        return self.token_data

    def get_logo(self):
        return ""

    def get_link(self):
        return self.link

    def get_code(self):
        if bool(self.link):
            # Format of link: https://piraidev.atlassian.net/browse/WAT-145
            link_array = self.link.split("/browse/")
            if len(link_array) == 2:
                return link_array[1]
        return None

    def get_type(self):
        return IntegrationType.TICKET
