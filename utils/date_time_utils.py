import datetime as dt


class DateTimeUtils:
    """
    Misc functions to deal with times
    """

    datetime_format = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def calculate_expiration_date_from_seconds(cls, expires_in) -> str:
        """
        Calculates an expiry date from an expires_in argument in seconds
        """
        expiration_date = dt.datetime.now() + dt.timedelta(seconds=expires_in)
        expiration_date_formatted = expiration_date.strftime(cls.datetime_format)
        return expiration_date_formatted

    @classmethod
    def current_datetime_as_string(cls):
        return dt.datetime.now().strftime(cls.datetime_format)

    @classmethod
    def current_date(cls):
        return dt.date.today()

    @classmethod
    def convert_string_date_to_date_only(cls, date: str):
        return dt.datetime.strptime(date, cls.datetime_format).date()
