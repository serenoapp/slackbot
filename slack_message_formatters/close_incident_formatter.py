from domain.incident import Incident


class CloseIncidentFormatter:
    """
    Shows a modal on slack with an input to set the incident resolution.
    """

    def format(self, incident_id):
        response = {
            "view": {
                "type": "modal",
                "callback_id": "modal-identifier",
                "private_metadata": incident_id,
                "title": {"type": "plain_text", "text": "Close Incident"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "blocks": [
                    {
                        "type": "input",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "incident_resolution",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "What was the resolution?",
                            },
                        },
                        "label": {"type": "plain_text", "text": "Resolution"},
                    }
                ],
            }
        }
        return response
