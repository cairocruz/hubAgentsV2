"""
Tool for finding places using the PlacesService.
"""
from services.places_service import PlacesService

class PlacesTool:
    """
    A tool that uses PlacesService to find and format places.
    """

    def __init__(self, service: PlacesService):
        """
        Initializes the PlacesTool with a PlacesService instance.

        Args:
            service (PlacesService): An instance of PlacesService.
        """
        self.service = service

    def search(self, query: str, location: str) -> str:
        """
        Searches for places and returns a formatted string.

        Args:
            query (str): The search query.
            location (str): The location to search near.

        Returns:
            str: A formatted string of the search results.
        """
        places = self.service.find_places(query, location)
        return self.service.format_places(places)
