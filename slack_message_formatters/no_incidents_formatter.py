from domain.incident import Incident


class NoIncidentsFormatter:
    """"""

    def build_response(self):
        response = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":clap: No ongoing incidents today!",
                    },
                }
            ]
        }
        return response
