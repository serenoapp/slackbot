import datetime as dt


class TokenData:

    """
    Class to save token data coming from an oauth request.
    It represents an oauth response. Contains access_token, refresh_token, and expiry date.
    """

    datetime_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self, access_token, refresh_token, expiry_date):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expiry_date = expiry_date

    def is_access_token_expired(self) -> bool:
        datetime_formatted = dt.datetime.strptime(
            self.expiry_date, self.datetime_format
        )
        return datetime_formatted <= dt.datetime.now()

    def is_valid(self) -> bool:
        return (
            bool(self.access_token)
            and bool(self.refresh_token)
            and bool(self.expiry_date)
        )
