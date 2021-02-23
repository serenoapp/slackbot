"""
Actions related to Users
"""
from typing import List
from services.integrated_service import IntegratedService
from services.jira_api_service import JiraApiService
from services.zoom_api_service import ZoomApiService
from utils.dynamo import DynamoUtils


class UserService:
    """
    Service to deal with users
    """
    @staticmethod
    def get_integrated_services(user_id) -> List[IntegratedService]:
        """
        Get services the user has integrated with
        """
        integrated_services: List[IntegratedService] = []
        apps = DynamoUtils.get_authorized_apps(user_id)
        if "jira" in apps:
            integrated_services.append(JiraApiService(user_id))
        if "zoom" in apps:
            integrated_services.append(ZoomApiService(user_id))
        return integrated_services
