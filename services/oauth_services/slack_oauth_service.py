import os
import requests
from dotenv import load_dotenv

load_dotenv()


class SlackOauthService:
    """
    Service to handle slack oauth calls and actions
    """

    SLACK_OAUTH_URL = "https://slack.com/api/oauth.v2.access"

    @classmethod
    def get_access_token(cls, code):
        """Returns access token together with the team id for slack"""
        request_body = cls.__build_access_token_request(code)
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        r = requests.post(cls.SLACK_OAUTH_URL, headers=headers, data=request_body)

        json_response = r.json()
        if json_response.get("ok") is not None and json_response.get("ok") is False:
            raise Exception(
                f"Unsuccessful response from slack oauth call {json_response}"
            )
        access_token = json_response.get("access_token")
        team = json_response.get("team")
        team_id = team.get("id")
        return team_id, access_token

    @classmethod
    def __build_access_token_request(cls, code):
        request_body = {
            "client_id": os.environ["SLACK_CLIENT_ID"],
            "client_secret": os.environ["SLACK_CLIENT_SECRET"],
            "code": code,
        }
        return request_body
