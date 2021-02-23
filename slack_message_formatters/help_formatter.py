from domain.incident import Incident


class HelpFormatter:
    """"""

    def format(self):
        response = {
            # "response_type": "in_channel",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Hey there 👋 I'm Sereno. I'm here to show you how we can interact with each other. First let's see the commands you can send me",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "• `/sereno register` This command will show you a list of apps you can integrate with me. For example: zoom, jira, pagerduty. etc.",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "• `/sereno responders list` This command will show you the list of responders. When a new incident is created, a user set as responder will be added to the incident channel. If a channel is set as responder, that channel will get a notification when an incident is created.",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "• `/sereno responders add @username` This command will add a user to the list of responders. You can concatenate as many users as you want in one command.",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "• `/sereno responders add #channel` This command will add achannel to the list of responders. You can concatenate as many channels or users as you want in one command.",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "• `/sereno set oncall @username` This command will set the oncall person. To get who is set as oncall you can tag me asking me this question. For exampe: `@Sereno who's oncall?`. The oncall will also be added to an incident channel.",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "• `/sereno close incident` I'll close the incident and log a closing line into the associated jira ticket. This will work inside an incident channel",
                    },
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "You can also tag me asking me questions or telling me things to do",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "• `@Sereno new incident` By telling me this, I'll create a new incident. I'll create an incident channel, inbolve the appropriate people, and work with the integrations you set up.",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "• `LOG: <any text>` If you have a jira integration, I'll log anything you add after the LOG: command into the jira ticket associated to the incident. This will work inside an incident channel",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "• `@Sereno who's oncall` I'll tell you who's the oncall",
                    },
                },
            ]
        }
        return response
