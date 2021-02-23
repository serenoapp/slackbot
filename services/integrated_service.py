"""Abstract class to represent a service that has been integrated"""
from abc import ABC, abstractmethod
from utils.integration_enum import IntegrationType


class IntegratedService(ABC):
    """
    Abstract class that represents a Call service, it could be Zoom, Meet, etc.
    """

    @abstractmethod
    def get_type(self) -> IntegrationType:
        """Get type of integrate service, based on IntegrationType enum"""
        pass
