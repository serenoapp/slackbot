"""TicketService implementation for Jira"""
import json
import logging
from datetime import date
import requests
from utils.dynamo import DynamoUtils
from domain.integrations.jira import Jira
from services.oauth_services.jira_oauth_service import JiraOauthService
from services.ticket_service import TicketService


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class JiraApiService(TicketService):
    """
    Service to handle jira api calls
    """

    BASE_URL = "https://%s.atlassian.net/rest/api/2"
    JIRA_TICKET_BASE_URL = "https://%s.atlassian.net/browse"

    def __init__(self, team_id) -> None:
        self.team_id = team_id
        self.jira: Jira = DynamoUtils.get_jira_data(team_id)
        if self.jira is None or not self.jira.is_valid():
            raise Exception("No ticket integration for team")
        self.BASE_URL = self.BASE_URL % self.jira.account_id
        self.JIRA_TICKET_BASE_URL = self.JIRA_TICKET_BASE_URL % self.jira.account_id

    def create_ticket(self):
        today = date.today()
        headers = self.__create_request_header()
        request_body = self.__build_issue_request(today.strftime("%b-%d-%Y"))
        r = requests.post(
            f"{self.BASE_URL}/issue/", headers=headers, data=json.dumps(request_body)
        )

        if r.status_code == 201:
            ticket_number = r.json()["key"]
            url_ticket = self.__get_ticket_url(ticket_number)
            self.jira.link = url_ticket
            return self.jira
        else:
            logger.error(f"Jira ticket could not be created {self.team_id}")
            return None

    def add_comment(self, ticket_id, comment):
        headers = self.__create_request_header()
        request_body = self.__build_comment_request(comment)
        r = requests.post(
            f"{self.BASE_URL}/issue/{ticket_id}/comment",
            headers=headers,
            data=json.dumps(request_body),
        )

        response = {"response_code": r.status_code}
        if r.status_code == 201:
            response["success"] = True
        else:
            response["descriptive_error"] = "Comment request to Jira returned an error"
        return response

    def __get_ticket_url(self, ticket_number):
        return f"{self.JIRA_TICKET_BASE_URL}/{ticket_number}"

    def __create_request_header(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + self.__get_access_token(),
        }
        return headers

    def __build_issue_request(self, issue_date):
        request_body = {
            "fields": {
                "project": {"key": "WAT"},
                "summary": f"Incident {issue_date}",
                "description": "Outage",
                "issuetype": {"name": "Task"},
            }
        }
        return request_body

    def __build_comment_request(self, comment):
        request_body = {"body": comment}
        return request_body

    def __get_access_token(self) -> str:
        """
        Gets access token from self.token_data.access_token if not expired.
        If access_token is expired, refreshes and saves the new token data
        """
        if (
            self.jira.token_data.expiry_date is not None
            and self.jira.token_data.is_access_token_expired() is False
        ):
            return self.jira.token_data.access_token
        else:
            logger.info(f"Token expired, refreshing... {self.team_id}")
            self.jira.token_data = JiraOauthService.refresh_access_token(
                self.jira.token_data
            )
            DynamoUtils.save_jira_data(self.team_id, self.jira)
            logger.info(f"Token refreshed and saved {self.team_id}")
            return self.jira.token_data.access_token
