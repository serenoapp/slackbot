"""Service to deal with incidents"""
from typing import List, cast
import logging
from domain.incident import Incident, IncidentStatus
from domain.integrations.integration import Integration
from services.ticket_service import TicketService
from services.call_service import CallService
from services.integrated_service import IntegratedService
from utils.integration_enum import IntegrationType
from utils.dynamo import DynamoUtils


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class IncidentService:
    """
    Class that handles incident actions
    """

    def __init__(self, team_id, integrated_services: List[IntegratedService]):
        self.team_id = team_id
        self.__set_integrated_services(integrated_services)

    def create_incident(self, incident_id, incident_name) -> Incident:
        """
        Creates an incident in the database
        Parameters:
            incident_id: In the slackbot context, this is the channel id
            incident_name: Name that will be set as a channel name and also saved in the db
        """
        # Create ticket
        ticket: Integration = self.create_ticket()

        # Create call
        call: Integration = self.create_call()

        incident = Incident(self.team_id, incident_id, incident_name)
        if ticket is not None:
            incident.set_ticket(ticket)
        if call is not None:
            incident.set_call(call)

        # Save incident
        DynamoUtils.create_incident(incident)
        return incident

    def get_call(self, incident_id) -> str:
        """Returns the call link for the given incident"""
        incident: Incident = DynamoUtils.get_incident(self.team_id, incident_id)
        if incident is not None and incident.has_call():
            return incident.call.get_link()
        return ""

    def get_ongoing_incidents(self) -> List[Incident]:
        """Returns all the incidents that are ongoing"""
        return DynamoUtils.get_ongoing_incidents(self.team_id)

    def get_today_incidents(self) -> List[Incident]:
        """Returns all incidents from today that are ongoing"""
        return DynamoUtils.get_today_incidents(self.team_id)

    # TODO - should also receive some text with the incident resolution and save in the DB
    def close_incident(self, incident_id):
        """Closes incident"""
        incident = Incident(self.team_id, incident_id)
        return DynamoUtils.update_incident_status(incident, IncidentStatus.CLOSED)

    def log_comment(self, incident_id: str, text: str) -> dict:
        """
        Adds a comment to the ticket associated to the incident_id received in the arguments
        """
        try:

            incident: Incident = DynamoUtils.get_incident(self.team_id, incident_id)
            if incident is None:
                return {
                    "status": "failure",
                    "failure_description": "Not ongoing incident in this channel, "
                    "please run this command in an incident channel",
                }
            if incident.has_ticket():
                issue_id = incident.ticket.get_link().split("browse/")[1]
                response = self.ticket_service.add_comment(issue_id, text)
                if (
                    response.get("success") is not None
                    and response.get("success") is True
                ):
                    return {"status": "ok"}
                else:
                    return {
                        "status": "failure",
                        "failure_description": response.get("descriptive_error"),
                    }
            else:
                return {
                    "status": "failure",
                    "failure_description": "No ticket associated to this incident",
                }
        except Exception as e:
            logger.error(f"could not log comment for team {self.team_id} - {e}")
            return {"status": "failure", "failure_description": "Could not log comment"}

    def create_ticket(self) -> Integration:
        """Creates a ticket for the incident"""
        if not hasattr(self, "ticket_service"):
            logger.error(f"no ticket integration for team {self.team_id}")
            return None
        logger.info("Creating ticket...")
        ticket: Integration = self.ticket_service.create_ticket()
        if ticket is not None:
            logger.info("Ticket created")
            return ticket
        else:
            logger.error(f"ticket could not be created for team {self.team_id}")
            return None

    def create_call(self) -> Integration:
        """Creates a call for the incident"""
        if not hasattr(self, "call_service"):
            logger.error(f"no call integration for team {self.team_id}")
            return None
        logger.info(f"Creating call... {self.team_id}")
        call: Integration = self.call_service.create_call()
        if call is not None:
            logger.info(f"call created {self.team_id}")
            return call
        else:
            logger.error(f"call could not be created {self.team_id}")
            return None

    def __set_integrated_services(self, integrated_services: List[IntegratedService]):
        """Sets in instance variables the integrated services being used"""
        for integrated_service in integrated_services:
            if integrated_service.get_type() == IntegrationType.CALL:
                self.call_service: CallService = cast(CallService, integrated_service)
            if integrated_service.get_type() == IntegrationType.TICKET:
                self.ticket_service: TicketService = cast(
                    TicketService, integrated_service
                )
