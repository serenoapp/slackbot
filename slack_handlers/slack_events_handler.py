import logging
from datetime import date
from typing import List
from slack_sdk.errors import SlackApiError
from slack_sdk.web.slack_response import SlackResponse
from domain.incident import Incident
from domain.slack_responder import SlackResponder
from domain.integrations.integration import Integration
from slack_message_formatters.current_incidents_formatter import (
    CurrentIncidentsFormatter,
)
from slack_message_formatters.create_incident_confirm_formatter import (
    CreateIncidentConfirmFormatter,
)
from slack_message_formatters.no_incidents_formatter import NoIncidentsFormatter
from slack_message_formatters.new_incident_integrations_links import (
    NewIncidentFormatter,
)
from services.incident_service import IncidentService
from services.responders_service import RespondersService
from services.user_service import UserService
from services.integrated_service import IntegratedService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SlackEventsHandler:
    """
    Class to handle events from slack
    """
    def __init__(self, client, team_id):
        self.slack_client = client
        self.team_id = team_id
        self.incident_name = ""
        integrated_services: List[
            IntegratedService
        ] = UserService.get_integrated_services(team_id)
        self.incident_service = IncidentService(team_id, integrated_services)
        self.responders_service = RespondersService(team_id)

    def handle_new_incident_creation(self, channel, incident_name):
        """
        Check whether there are already ongoing incidents today.
        If there are ongoing incidents, validate with user if a new incident has to be created.
        If there are no ongoing incidents, create a new incident.
        """
        self.incident_name = incident_name
        incidents: List[Incident] = self.incident_service.get_ongoing_incidents()
        today_ongoing_incidents = [i for i in incidents if i.is_from_today() is True]
        if len(today_ongoing_incidents) == 0:  # no incidents today
            self.create_new_incident(channel, incident_name)
        else:
            response = self.show_ongoing_incidents_message(today_ongoing_incidents)
            self.slack_client.chat_postMessage(channel=channel, blocks=response)

    # Investigate how to make this function transactional
    def create_new_incident(self, channel, incident_name):
        """Will create a channel, and call incident service to start the incident workflow"""
        self.incident_name = incident_name
        self.slack_client.chat_postMessage(
            channel=channel, text="Ack... creating a new incident channel"
        )
        try:
            self.__create_new_incident(incident_name, channel)
        except Exception as e:  # TODO - if it's name taken, we should somehow recover and create the channel anyway!!
            logger.error(f"Could not create incident - {e}")
            self.slack_client.chat_postMessage(
                channel=channel,
                text=f"This is embarrassing... There was an error whilst creating the incident {e}",
            )

    def show_ongoing_incidents_message(self, incidents):
        formatter = CreateIncidentConfirmFormatter(self.incident_name)
        response = formatter.format(incidents)
        return response.get("blocks")

    def log_comment(self, incident_id: str, text: str):
        response = self.incident_service.log_comment(incident_id, text)
        if "ok" not in response["status"]:
            self.slack_client.chat_postMessage(
                channel=incident_id, text=response.get("failure_description")
            )

    def get_oncall(self, team_id):
        return self.responders_service.get_oncall(team_id)

    def get_ongoing_incidents_from_today(self, _team_id):
        incidents: List[Incident] = self.incident_service.get_ongoing_incidents()
        today_incidents = [i for i in incidents if i.is_from_today() is True]
        if len(today_incidents) == 0:
            formatter = NoIncidentsFormatter()
            response = formatter.build_response()
            return response.get("blocks")
        formatter = CurrentIncidentsFormatter()
        response = formatter.build_response(today_incidents)
        return response.get("blocks")

    def close_incident_and_add_resolution(self, channel_id, resolution_text):
        close_incident_response = self.close_incident(
            channel_id
        )  # TODO - add the resolution to the incidents table too!
        if close_incident_response is None:
            self.slack_client.chat_postMessage(
                channel=channel_id,
                text="Error: trying to close a non existent incident!!",
            )
            return
        self.slack_client.chat_postMessage(channel=channel_id, text="Incident closed!")
        self.log_comment(channel_id, resolution_text)

    def close_incident(self, channel_id):
        return self.incident_service.close_incident(channel_id)

    def create_ticket(self) -> Integration:
        return self.incident_service.create_ticket()

    def create_call(self) -> Integration:
        return self.incident_service.create_call()

    def get_call(self, incident_id):
        return self.incident_service.get_call(incident_id)

    def __create_new_incident(self, incident_name, calling_channel) -> dict:
        # Create channel
        channel_name = self.__build_channel_name(incident_name)
        response = self.__create_channel(channel_name, calling_channel)
        if response.get("status") != "ok":
            raise Exception("Error creating channel")
        channel_id = response.get("channel_id")

        try:
            logger.info(f"Creating incident... {self.team_id}")
            # Create incident
            incident: Incident = self.incident_service.create_incident(
                channel_id, incident_name
            )

            integrations: List[Integration] = []

            if incident.ticket is not None:
                integrations.append(incident.ticket)
            if incident.call is not None:
                integrations.append(incident.call)

            oncall = self.responders_service.get_oncall(self.team_id)
            formatter = NewIncidentFormatter()
            self.slack_client.chat_postMessage(
                channel=channel_id,
                blocks=formatter.build_response(incident, integrations, oncall).get(
                    "blocks"
                ),
            )
            if bool(incident.name.strip()):
                self.slack_client.conversations_setTopic(
                    channel=channel_id, topic=incident.name
                )
            elif incident.has_call():
                self.slack_client.conversations_setTopic(
                    channel=channel_id, topic=incident.call.get_link()
                )

            self.__notify_responders(channel_id, incident, integrations, oncall)
            logger.info(f"Creating incident done... {self.team_id}")
            return {"status": "ok"}
        except Exception as e:
            logger.error(f"incident could not be created {self.team_id} {e}")
            return {"status": "failed"}

    def __build_channel_name(self, incident_name):
        today = date.today()
        today_format = today.strftime("%d-%m-%y")
        incident_name = (
            incident_name.strip().replace(" ", "-").lower()
        )  # adding '-' for slack channel format
        channel_name = ""
        if incident_name != "":
            channel_name = f"i-{incident_name[:14]}-{today_format}"
        else:
            today_incidents = self.incident_service.get_today_incidents()
            number_of_incidents = len(today_incidents)
            channel_name = f"i-sereno-{today_format}_{str(number_of_incidents + 1)}"
        return channel_name

    def __create_channel(self, channel_name, calling_channel) -> dict:
        try:
            response = self.slack_client.conversations_create(name=channel_name)
            if (
                response.get("channel") is None
                or response.get("channel").get("id") is None
            ):
                self.__handle_channel_creation_error(calling_channel)
                return {"status": "failure"}
            channel_id = response.get("channel").get("id")
            if channel_id is None:
                self.__handle_channel_creation_error(calling_channel)
                return {"status": "failure"}
            message = "Channel created - <#%s>" % channel_id
            self.slack_client.chat_postMessage(channel=calling_channel, text=message)
            return {"status": "ok", "channel_id": channel_id}
        except SlackApiError as e:
            self.__handle_channel_creation_error(calling_channel, e)
            return {"status": "failure"}

    def __handle_channel_creation_error(self, calling_channel, exception=None):
        message = f"Incident channel could not be created for team {self.team_id}"
        self.slack_client.chat_postMessage(channel=calling_channel, text=message)
        if exception is not None:
            logger.error(
                f"slack channel could not be created for team {self.team_id} {exception}"
            )
        else:
            logger.error(f"slack channel could not be created for team {self.team_id}")

    def __notify_responders(self, channel_id, incident, integrations, oncall) -> None:
        responders: List[
            SlackResponder
        ] = self.responders_service.get_responders_with_oncall()
        user_responders = []
        channel_responders = []
        responder: SlackResponder
        for responder in responders:
            if responder.is_user():
                user_responders.append(responder.id)
            elif responder.is_channel():
                channel_responders.append(responder)

        # add user responders to new channel
        if len(user_responders) > 0:
            self.slack_client.conversations_invite(
                channel=channel_id, users=user_responders
            )

        for responder in channel_responders:
            slack_response: SlackResponse = self.slack_client.conversations_join(
                channel=responder.id
            )
            if slack_response.get("ok") is True:
                formatter = NewIncidentFormatter()
                self.slack_client.chat_postMessage(
                    channel=responder.id,
                    blocks=formatter.build_response(incident, integrations, oncall).get(
                        "blocks"
                    ),
                )
