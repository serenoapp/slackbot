from domain.incident import Incident


class CreateIncidentConfirmFormatter:
    """
    This class will format the message to show in slack when a user wants to create an incident and there's already one on going.
    It contains interactive elements ("Create incident" and "Cancel" buttons) to confirm actions.
    """

    def __init__(self, incident_name):
        if incident_name is not None and incident_name != "":
            self.incident_name = incident_name
        else:
            self.incident_name = " "

    def format(self, incidents):
        response = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":eyes: There are already incidents opened *TODAY* \n \n Do you still wish to create a new incident?",
                    },
                },
                {"type": "divider"},
            ]
        }

        for incident in incidents:
            response["blocks"].append(self.__incident_section(incident))
            response["blocks"].append({"type": "divider"})
        response.get("blocks").append(self.__add_action_buttons())
        return response

    def __incident_section(self, incident: Incident) -> dict:
        incident_section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*<#{incident.incident_id}>*\n*Started at*: {incident.started_datetime}\n*Status*: {incident.status}",
            },
        }
        return incident_section

    def __add_action_buttons(self):
        actions = {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Create new incident",
                    },
                    "style": "primary",
                    "action_id": "create_incident",
                    "value": self.incident_name,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "emoji": True, "text": "Cancel"},
                    "style": "danger",
                    "action_id": "cancel",
                },
            ],
        }
        return actions
