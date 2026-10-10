from abc import ABC, abstractmethod
from typing import List
from app.core.schemas import FareObservationCreate

class BaseCollector(ABC):
    """
    Abstract interface for all fare data collection adapters.
    Ensures that real scrapers, third-party APIs, and mock generators
    all produce strictly validated FareObservationCreate schemas.
    """

    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    def fetch_fares(self, origin: str, destination: str, days_ahead: int) -> List[FareObservationCreate]:
        """
        Fetch fares for a given route and booking advance window.
        
        :param origin: 3-letter IATA code (e.g., 'BOM')
        :param destination: 3-letter IATA code (e.g., 'DEL')
        :param days_ahead: Advance purchase window (e.g., 7 days before departure)
        :return: List of FareObservationCreate instances
        """
        pass