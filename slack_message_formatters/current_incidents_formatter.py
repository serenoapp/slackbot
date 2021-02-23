from domain.incident import Incident


class CurrentIncidentsFormatter:
    def build_response(self, incidents):
        response = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":rotating_light: These are the *ONGOING* incidents from *TODAY* :rotating_light:",
                    },
                },
                {"type": "divider"},
            ]
        }

        for incident in incidents:
            response["blocks"].append(self.__incident_section(incident))
            response["blocks"].append({"type": "divider"})
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
