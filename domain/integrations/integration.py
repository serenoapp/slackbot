from abc import ABC, abstractmethod
from domain.token_data import TokenData


class Integration(ABC):
    @abstractmethod
    def get_link(self) -> str:
        pass

    @abstractmethod
    def get_logo(self) -> str:
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def get_token_data(self) -> TokenData:
        pass

    @abstractmethod
    def get_code(self):
        """
        Returns the identifier. For a call should be the call id, for a ticket a ticket id, etc
        """
        pass

    @abstractmethod
    def get_type(self):
        None
