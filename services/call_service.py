from abc import ABC, abstractmethod
from domain.integrations.integration import Integration
from services.integrated_service import IntegratedService
from utils.integration_enum import IntegrationType


class CallService(IntegratedService):
    """
    Abstract class that represents a Call service, it could be Zoom, Meet, etc.
    """

    @abstractmethod
    def create_call(self) -> Integration:
        pass

    def get_type(self) -> IntegrationType:
        return IntegrationType.CALL
