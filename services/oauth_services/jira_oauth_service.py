import os
import json
import logging
import requests
from utils.date_time_utils import DateTimeUtils
from domain.token_data import TokenData

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class JiraOauthService:
    """
    Service to handle jira oauth calls and actions
    """

    JIRA_OAUTH_ACCESS_CODE_URL = "https://auth.atlassian.com/authorize/"
    JIRA_OAUTH_ACCESS_TOKEN_URL = "https://auth.atlassian.com/oauth/token"
    JIRA_ID_REQUEST_URL = "https://api.atlassian.com/oauth/token/accessible-resources"
    JIRA_CLIENT_ID = os.environ["JIRA_CLIENT_ID"]
    JIRA_REDIRECT_URL = os.environ["JIRA_REDIRECT_URL"]

    @classmethod
    def get_jira_id(cls, access_token: str) -> str:
        """
        Makes a call to jira oauth api to retrieve the jira id (name of the account to use in the url to make api calls)
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + access_token,
        }
        r = requests.get(cls.JIRA_ID_REQUEST_URL, headers=headers)
        json_response = r.json()
        if len(json_response) == 0:
            logger.error("jira did not return any response for given access token")
            raise Exception()
        name = json_response[0].get("name")
        if name is None or name == "":
            logger.error("jira did not return any name/id for given access token")
            raise Exception()
        return name

    @classmethod
    def get_token_data(cls, code: str) -> TokenData:
        """
        Makes a call to jira oauth server and gets token data
        Response:
            TokenData contains access_token, refresh_token, expiry_date
        """
        request_body = cls.__build_access_token_request(code)
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        r = requests.post(
            cls.JIRA_OAUTH_ACCESS_TOKEN_URL,
            headers=headers,
            data=json.dumps(request_body),
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
    def refresh_access_token(cls, token_data: TokenData) -> TokenData:
        """
        Makes a call to jira oauth server to refresh the token
        Response:
            TokenData contains access_token, refresh_token, expiry_date
        """
        request_body = cls.__build_refresh_token_request(token_data.refresh_token)
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        r = requests.post(
            cls.JIRA_OAUTH_ACCESS_TOKEN_URL,
            headers=headers,
            data=json.dumps(request_body),
        )

        # TODO - handle errors and different responses
        json_response = r.json()
        access_token = json_response.get("access_token")
        refresh_token = (
            token_data.refresh_token
        )  # jira doesn't return a new refresh token, need to keep the current one
        expires_in = json_response.get("expires_in")
        expiry_date = DateTimeUtils.calculate_expiration_date_from_seconds(expires_in)
        oauth_token_response = TokenData(access_token, refresh_token, expiry_date)
        token_data = TokenData(
            oauth_token_response.access_token, refresh_token, expiry_date
        )
        return token_data

    @classmethod
    def __build_access_token_request(cls, code):
        request_body = {
            "grant_type": "authorization_code",
            "client_id": os.environ["JIRA_CLIENT_ID"],
            "client_secret": os.environ["JIRA_CLIENT_SECRET"],
            "code": code,
            "redirect_uri": cls.JIRA_REDIRECT_URL,
        }
        return request_body

    @classmethod
    def __build_refresh_token_request(cls, refresh_token: str) -> dict:
        request_body = {
            "grant_type": "refresh_token",
            "client_id": os.environ["JIRA_CLIENT_ID"],
            "client_secret": os.environ["JIRA_CLIENT_SECRET"],
            "refresh_token": refresh_token,
        }
        return request_body
