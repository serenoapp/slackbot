class SlackResponder:
    """
    Represents a responder in slack that needs to be notified
    If it's a user, the id will start with a U
    If it's a channel, the id will start with a C
    """

    def __init__(self, responder_id: str):
        self.id = responder_id

    def is_user(self) -> bool:
        return self.id[0] == "U"

    def is_channel(self) -> bool:
        return self.id[0] == "C"
