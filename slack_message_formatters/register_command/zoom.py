import os
import logging
from requests.auth import HTTPBasicAuth
import requests
from domain.token_data import TokenData
import urllib
from utils.date_time_utils import DateTimeUtils
from slack_message_formatters.register_command.integrated_service import (
    IntegratedServiceFormatter,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Zoom(IntegratedServiceFormatter):

    # ZOOM_OAUTH_ACCESS_CODE_URL =
    ZOOM_OAUTH_ACCESS_TOKEN_URL = "https://zoom.us/oauth/token"
    ZOOM_REDIRECT_URL = os.environ["ZOOM_REDIRECT_URI"]

    @classmethod
    def get_token_data(cls, code: str) -> TokenData:
        """
        Makes a call to zoom oauth server and gets token data
        Response:
            TokenData contains access_token, refresh_token, expiry_date
        """
        request_body = cls.__build_access_token_request(code)
        r = requests.post(
            cls.ZOOM_OAUTH_ACCESS_TOKEN_URL,
            data=request_body,
            auth=HTTPBasicAuth(
                os.environ["ZOOM_CLIENT_ID"], os.environ["ZOOM_CLIENT_SECRET"]
            ),
        )

        # TODO - handle errors and different responses
        json_response = r.json()
        access_token = json_response.get("access_token")
        refresh_token = json_response.get("refresh_token")
        expires_in = json_response.get("expires_in")
        expiry_date = DateTimeUtils.calculate_expiration_date_from_seconds(expires_in)
        token_data = TokenData(access_token, refresh_token, expiry_date)
        return token_data

    @classmethod
    def __build_access_token_request(cls, code):
        request_body = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": cls.ZOOM_REDIRECT_URL,
        }
        return request_body

    @classmethod
    def refresh_access_token(cls, token_data: TokenData) -> TokenData:
        """
        Makes a call to zoom oauth server to refresh the token
        Response:
            TokenData contains access_token, refresh_token, expiry_date
        """
        # TODO: get refresh token properly
        request_body = cls.__build_refresh_token_request(token_data.refresh_token)
        r = requests.post(
            cls.ZOOM_OAUTH_ACCESS_TOKEN_URL,
            data=request_body,
            auth=HTTPBasicAuth(
                os.environ["ZOOM_CLIENT_ID"], os.environ["ZOOM_CLIENT_SECRET"]
            ),
        )
        if r.status_code == 200:
            json_response = r.json()
            access_token = json_response.get("access_token")
            refresh_token = json_response.get("refresh_token")
            expires_in = json_response.get("expires_in")
            expiry_date = DateTimeUtils.calculate_expiration_date_from_seconds(
                expires_in
            )
            oauth_token_response = TokenData(access_token, refresh_token, expiry_date)
            token_data = TokenData(
                oauth_token_response.access_token, refresh_token, expiry_date
            )
            return token_data
        else:
            logger.error("failed with code: " + str(r.status_code))
            return None

    def build_oauth_entry(self, teamId, userId, authorized_apps):
        zoom = []
        zoom_section = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "* 2️⃣ Zoom*"},
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Register",
                },
                "url": self.build_access_code_link(teamId, userId),
                "value": "zoom",
            },
        }
        zoom.append(zoom_section)

        if "zoom" in authorized_apps:
            zoom_registered = super().build_already_registered_item()
            zoom.append(zoom_registered)

        return zoom

    def build_access_code_link(self, teamId, userId):
        state = "&state=" + super().build_state_param(teamId, userId)
        redirect_url = urllib.parse.quote(self.ZOOM_REDIRECT_URL, safe="")
        return (
            f"https://zoom.us/oauth/authorize?client_id=DkZ7MOwzTkChDt5otH0EA&response_type=code&redirect_uri={redirect_url}"
            + state
        )

    @classmethod
    def __build_refresh_token_request(cls, refresh_token: str) -> dict:
        request_body = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        return request_body
