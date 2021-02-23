"""
Call service implementation for zoom
"""
import json
import logging
import requests
from domain.integrations.zoom import Zoom
from domain.integrations.integration import Integration
from utils.dynamo import DynamoUtils
from services.oauth_services.zoom_oauth_service import ZoomOauthService
from services.call_service import CallService


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ZoomApiService(CallService):
    """
    Service to handle zoom api calls
    """

    ZOOM_API_URL = "https://api.zoom.us/v2/users/"
    ZOOM_GET_USER_API = "https://api.zoom.us/v2/users/me"

    def __init__(self, team_id):
        self.team_id = team_id
        self.zoom: Zoom = DynamoUtils.get_zoom_data(team_id)
        if not self.zoom.is_valid():
            raise Exception("No call integration for team")

    def __create_request_header(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.__get_access_token(),
        }
        return headers

    def create_call(self) -> Integration:
        try:
            headers = self.__create_request_header()
            user_id = self.__get_user_id(headers)
            if user_id is None:
                return None
            request_body = {
                "type": 2,
                "settings": {"join_before_host": True, "jbh_time": 0},
            }
            r = requests.post(
                self.ZOOM_API_URL + user_id + "/meetings",
                headers=headers,
                data=json.dumps(request_body),
            )
            response = {"response_code": r.status_code}
            if r.status_code == 201:
                call_link = r.json().get("join_url")
                self.zoom.link = call_link
                return self.zoom
            else:
                logger.error(f"Zoom meeting could not be created {e}")
                return None
        except Exception as e:
            logger.error(f"Zoom meeting could not be created {e}")
            return None

    def __get_user_id(self, headers):
        r = requests.get(self.ZOOM_GET_USER_API, headers=headers)
        return r.json().get("id")

    def __get_access_token(self) -> str:
        """
        Gets access token from self.token_data.access_token if not expired.
        If access_token is expired, refreshes and saves the new token data
        """
        if (
            self.zoom.token_data.expiry_date is not None
            and self.zoom.token_data.is_access_token_expired() is False
        ):
            return self.zoom.token_data.access_token
        else:
            if self.zoom.token_data.refresh_token is not None:
                logger.info("Token expired, refreshing...")
                self.zoom.token_data = ZoomOauthService.refresh_access_token(
                    self.zoom.token_data
                )
                DynamoUtils.save_zoom_data(self.team_id, self.zoom)
                logger.info("Token refreshed and saved")
                return self.zoom.token_data.access_token
            else:
                raise Exception()
