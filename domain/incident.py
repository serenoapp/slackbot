import enum
from utils.date_time_utils import DateTimeUtils
from domain.integrations.integration import Integration


class Incident:
    """ "
    Class that represents an incident
    """

    def __init__(self, team_id, channel_id, name=""):
        self.team_id = team_id
        self.incident_id = channel_id
        self.name = name
        self.status = IncidentStatus.ONGOING
        self.started_datetime = DateTimeUtils.current_datetime_as_string()
        self.ticket: Integration = None
        self.call: Integration = None

    @staticmethod
    def build_from_dict(input_dict: dict):
        incident = Incident(
            input_dict.get("teamId"),
            input_dict.get("incidentId"),
            input_dict.get("name"),
        )
        incident.status = input_dict.get("status")  # TODO - use value of for enum!
        incident.started_datetime = input_dict.get("started_datetime")
        return incident

    def set_call(self, call: Integration):
        self.call = call

    def set_ticket(self, ticket: Integration):
        self.ticket = ticket

    def is_from_today(self):
        if self.started_datetime is not None:
            incident_started = DateTimeUtils.convert_string_date_to_date_only(
                self.started_datetime
            )
            today = DateTimeUtils.current_date()
            return incident_started == today
        return False

    def has_ticket(self):
        return self.ticket and bool(self.ticket.get_link())

    def has_call(self):
        return self.call and bool(self.call.get_link())


class IncidentStatus(enum.Enum):
    ONGOING = "ONGOING"
    MITIGATED = "MITIGATED"
    CLOSED = "CLOSED"
