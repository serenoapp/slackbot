import os
import logging
from typing import List
from boto3.dynamodb.conditions import Key
from utils.aws import AwsUtils
from domain.incident import Incident
from domain.integrations.jira import Jira
from domain.integrations.zoom import Zoom
from domain.token_data import TokenData
from domain.incident import IncidentStatus

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DynamoUtils:
    """Utils class to handle DynamoDB operations"""

    USERS_TABLE = os.environ["USERS_TABLE"]
    INCIDENTS_TABLE = os.environ["INCIDENTS_TABLE"]
    DYNAMO_RESOURCE = AwsUtils.get_dynamodb_resource()

    users_table = DYNAMO_RESOURCE.Table(USERS_TABLE)
    incidents_table = DYNAMO_RESOURCE.Table(INCIDENTS_TABLE)

    @classmethod
    def save_jira_data(cls, team_id, jira: Jira):
        response = cls.users_table.update_item(
            Key={
                "teamId": team_id,
            },
            UpdateExpression="set apps.jira = :new_app",
            ExpressionAttributeValues={
                ":new_app": {
                    "id": jira.account_id,
                    "access_token": jira.token_data.access_token,
                    "refresh_token": jira.token_data.refresh_token,
                    "expiry_date": jira.token_data.expiry_date,
                }
            },
        )
        return response

    @classmethod
    def save_zoom_data(cls, team_id, zoom: Zoom):
        response = cls.users_table.update_item(
            Key={
                "teamId": team_id,
            },
            UpdateExpression="set apps.zoom = :new_app",
            ExpressionAttributeValues={
                ":new_app": {
                    "access_token": zoom.token_data.access_token,
                    "refresh_token": zoom.token_data.refresh_token,
                    "expiry_date": zoom.token_data.expiry_date,
                }
            },
        )
        return response

    @classmethod
    def save_slack_access_token(cls, team_id, access_token):
        response = cls.users_table.update_item(
            Key={
                "teamId": team_id,
            },
            UpdateExpression="SET access_token=:access_token, apps=if_not_exists(apps, :apps)",
            ExpressionAttributeValues={":access_token": access_token, ":apps": {}},
        )
        return response

    @classmethod
    def save_responders(cls, team_id, responders):
        response = cls.users_table.update_item(
            Key={
                "teamId": team_id,
            },
            UpdateExpression="ADD responders :responders",
            ExpressionAttributeValues={":responders": set(responders)},
            ReturnValues="UPDATED_NEW",
        )
        return response

    @classmethod
    def save_oncall(cls, team_id, user_id):
        response = cls.users_table.update_item(
            Key={
                "teamId": team_id,
            },
            UpdateExpression="SET oncall=:oncall",
            ExpressionAttributeValues={":oncall": user_id},
        )
        return response

    @classmethod
    def get_oncall(cls, team_id):
        try:
            response = cls.users_table.get_item(Key={"teamId": team_id})
            item = response["Item"]
            return item.get("oncall")
        except Exception as e:
            logger.error(f"Get_oncall {team_id} {e}")
            return "there was an error"

    @classmethod
    def remove_responders(cls, team_id, responders):
        response = cls.users_table.update_item(
            Key={
                "teamId": team_id,
            },
            UpdateExpression="DELETE responders :responders",
            ExpressionAttributeValues={":responders": set(responders)},
            ReturnValues="UPDATED_NEW",
        )
        return response

    @classmethod
    def create_incident(cls, incident: Incident):
        response = cls.incidents_table.put_item(
            Item={
                "teamId": incident.team_id,
                "name": incident.name,
                "incidentId": incident.incident_id,
                "callLink": incident.call.get_link()
                if incident.call is not None
                else "",
                "ticketLink": incident.ticket.get_link()
                if incident.ticket is not None
                else "",
                "status": incident.status.name,
                "started_datetime": incident.started_datetime,
            }
        )
        return response

    @classmethod
    def update_incident_status(
        cls, incident: Incident, incident_status: IncidentStatus
    ):
        try:
            response = cls.incidents_table.update_item(
                Key={"teamId": incident.team_id, "incidentId": incident.incident_id},
                UpdateExpression="SET #st=:incident_status",
                ConditionExpression="attribute_exists(teamId) and attribute_exists(incidentId)",
                ExpressionAttributeValues={":incident_status": incident_status.name},
                ExpressionAttributeNames={"#st": "status"},
            )
            return response
        except cls.DYNAMO_RESOURCE.meta.client.exceptions.ConditionalCheckFailedException as e:
            logger.error(f"trying to close a non existent incident {incident.team_id}")
            return None

    @classmethod
    def get_incident(cls, team_id: str, incident_id: str) -> Incident:
        response = cls.incidents_table.query(
            KeyConditionExpression="teamId = :teamId and incidentId = :incidentId",
            ExpressionAttributeValues={":teamId": team_id, ":incidentId": incident_id},
        )
        items = response["Items"]
        if len(items) == 1:
            incident_item = items[0]
            incident = Incident(team_id, incident_id, incident_item.get("name"))
            zoom = Zoom(None)
            zoom.link = incident_item.get("callLink")
            incident.set_call(zoom)
            jira = Jira(None, "")
            jira.link = incident_item.get("ticketLink")
            incident.set_ticket(jira)
            incident.started_datetime = incident_item.get("started_datetime")
            return incident
        else:
            return None

    @classmethod
    def get_ongoing_incidents(cls, team_id) -> List[Incident]:
        try:
            response = cls.incidents_table.query(
                KeyConditionExpression=Key("teamId").eq(team_id)
            )
            incidents = response["Items"]
            ongoing_incidents = cls.__filter_ongoing_incidents(incidents)
            return ongoing_incidents
        except Exception as e:
            logger.error(f"get_ongoing_incidents {team_id} {e}")
            return []

    @classmethod
    def get_today_incidents(cls, team_id) -> List[Incident]:
        try:
            response = cls.incidents_table.query(
                KeyConditionExpression=Key("teamId").eq(team_id)
            )
            incidents = response["Items"]
            today_incidents = cls.__filter_today_incidents(incidents)
            return today_incidents
        except Exception as e:
            logger.error(f"get_today_incidents {team_id} {e}")
            return []

    @classmethod
    def __filter_ongoing_incidents(cls, incidents: List) -> List:
        ongoing_incidents = []
        for incident_dict in incidents:
            if incident_dict.get("status") == IncidentStatus.ONGOING.name:
                incident = Incident.build_from_dict(incident_dict)
                ongoing_incidents.append(incident)
        return ongoing_incidents

    @classmethod
    def __filter_today_incidents(cls, incidents: List) -> List:
        today_incidents = []
        for incident_dict in incidents:
            incident = Incident.build_from_dict(incident_dict)
            if incident.is_from_today():
                today_incidents.append(incident)
        return today_incidents

    @classmethod
    def get_authorized_apps(cls, team_id):
        try:
            response = cls.users_table.get_item(Key={"teamId": team_id})
            item = response["Item"]
            apps = item["apps"]
            return apps
        except Exception as e:
            logger.error(f"get_authorized_apps {team_id} {e}")
            return "there was an error"

    @classmethod
    def get_slack_access_token(cls, team_id):
        try:
            response = cls.users_table.get_item(Key={"teamId": team_id})
            item = response["Item"]
            return item.get("access_token")
        except Exception as e:
            logger.error(f"get_slack_access_token {team_id} {e}")
            return "there was an error"

    @classmethod
    def get_zoom_data(cls, team_id) -> Zoom:
        try:
            apps: dict = cls.get_authorized_apps(team_id)
            zoom_dict: dict = apps["zoom"]
            token_data = TokenData(
                zoom_dict.get("access_token"),
                zoom_dict.get("refresh_token"),
                zoom_dict.get("expiry_date"),
            )
            zoom = Zoom(token_data)
            return zoom
        except Exception as e:
            logger.error(f"Get_zoom_data {team_id} {e}")
            return None

    @classmethod
    def get_jira_data(cls, team_id) -> Jira:
        try:
            apps: dict = cls.get_authorized_apps(team_id)
            jira_dict: dict = apps["jira"]
            token_data = TokenData(
                jira_dict.get("access_token"),
                jira_dict.get("refresh_token"),
                jira_dict.get("expiry_date"),
            )
            account_id = jira_dict.get("id")
            jira = Jira(token_data, account_id)
            return jira
        except Exception as e:
            logger.error(f"Get_jira_token_data {team_id} {e}")
            return None

    @classmethod
    def get_responders(cls, team_id):
        try:
            response = cls.users_table.get_item(Key={"teamId": team_id})
            item = response["Item"]
            if "responders" not in item:
                return []
            return item["responders"]
        except Exception as e:
            logger.error(f"Get_responders {team_id} {e}")
            return []
