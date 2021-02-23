from domain.integrations.integration import Integration
from domain.incident import Incident
from typing import List
from utils.integration_enum import IntegrationType


class NewIncidentFormatter:
    """"""

    def build_response(
        self, incident: Incident, integrations: List[Integration], oncall
    ):
        incident_name = incident.name if bool(incident.name) else "No description set"
        oncall = f"<@{oncall}>" if bool(oncall) else "No oncall set"
        response = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "A new incident has been opened",
                    },
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Incident:*\n{incident_name}"},
                        {"type": "mrkdwn", "text": f"*Oncall:*\n{oncall}"},
                        {
                            "type": "mrkdwn",
                            "text": f"*Channel:*\n<#{incident.incident_id}>",
                        },
                    ],
                },
            ]
        }

        fields = self.__build_links_section(integrations)
        if fields is not None:
            response.get("blocks").append(fields)
        return response

    def __build_links_section(self, integrations: List[Integration]):
        fields = []
        for integration in integrations:
            if integration.get_type() == IntegrationType.CALL and bool(
                integration.get_link()
            ):
                call_section = self.__build_call_section(integration)
                fields.append(call_section)
            if integration.get_type() == IntegrationType.TICKET and bool(
                integration.get_link()
            ):
                call_section = self.__build_ticket_section(integration)
                fields.append(call_section)
        if len(fields) > 0:
            return {"type": "section", "fields": fields}
        return None

    def __build_call_section(self, integration: Integration):
        return {"type": "mrkdwn", "text": f"Call\n<{integration.get_link()}|Join>"}

    def __build_ticket_section(self, integration: Integration):
        ticket_id = integration.get_code()
        section = {
            "type": "mrkdwn",
            "text": f"Ticket\n<{integration.get_link()}|{ticket_id}>",
        }
        return section
