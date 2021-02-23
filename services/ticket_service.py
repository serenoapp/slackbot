"""
Abstract class extending IntegratedService
"""
from abc import abstractmethod
from domain.integrations.integration import Integration
from services.integrated_service import IntegratedService
from utils.integration_enum import IntegrationType


class TicketService(IntegratedService):
    """
    Abstract class that represents a Ticket service, it could be Jira, Trello, etc.
    """

    @abstractmethod
    def create_ticket(self) -> Integration:
        """
        Creates a ticket
        """
        pass

    @abstractmethod
    def add_comment(self, ticket_id, comment):
        """
        Add comment to a ticket
        """
        pass

    def get_type(self) -> IntegrationType:
        """
        Get integration type based on enum IntegrationType
        """
        return IntegrationType.TICKET
