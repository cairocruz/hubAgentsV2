"""
Service to interact with Google Places API.
"""
import os
import googlemaps
from typing import List, Dict, Any

# It's recommended to use a more secure way to store the API key,
# such as environment variables or a secret management service.
# For this example, we'll use an environment variable.
API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")

class PlacesService:
    """
    A service to interact with the Google Places API.
    """

    def __init__(self, api_key: str = API_KEY):
        """
        Initializes the PlacesService with a Google Places API key.

        Args:
            api_key (str): The Google Places API key.
        """
        if not api_key:
            raise ValueError("Google Places API key is not set.")
        self.gmaps = googlemaps.Client(key=api_key)

    def find_places(
        self, query: str, location: str, radius: int = 5000
    ) -> List[Dict[str, Any]]:
        """
        Finds places near a given location based on a query.

        Args:
            query (str): The search query (e.g., "women's shelter", "hospital").
            location (str): The location to search near (e.g., "São Paulo, SP").
            radius (int, optional): The search radius in meters. Defaults to 5000.

        Returns:
            List[Dict[str, Any]]: A list of places found.
        """
        try:
            places_result = self.gmaps.places(
                query=query, location=location, radius=radius
            )
            return places_result.get("results", [])
        except Exception as e:
            print(f"Error finding places: {e}")
            return []

    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """
        Gets details for a specific place by its ID.

        Args:
            place_id (str): The ID of the place.

        Returns:
            Dict[str, Any]: The details of the place.
        """
        try:
            place_details = self.gmaps.place(
                place_id=place_id,
                fields=[
                    "name",
                    "formatted_address",
                    "formatted_phone_number",
                    "opening_hours",
                    "website",
                ],
            )
            return place_details.get("result", {})
        except Exception as e:
            print(f"Error getting place details: {e}")
            return {}

    def format_places(self, places: List[Dict[str, Any]]) -> str:
        """
        Formats a list of places into a human-readable string.

        Args:
            places (List[Dict[str, Any]]): A list of places.

        Returns:
            str: A formatted string of places.
        """
        if not places:
            return "Nenhum local de ajuda encontrado nas proximidades."

        emergency_services = []
        regular_services = []

        for place in places:
            details = self.get_place_details(place["place_id"])
            if not details:
                continue

            name = details.get("name", "N/A")
            address = details.get("formatted_address", "N/A")
            phone = details.get("formatted_phone_number", "N/A")
            opening_hours = details.get("opening_hours", {})
            is_24h = opening_hours.get("open_now", False) and len(opening_hours.get("periods", [])) == 1

            if is_24h:
                emergency_services.append(
                    f"• {name} - {address}\n• 📞 {phone}"
                )
            else:
                hours = "Horário não disponível"
                if "weekday_text" in opening_hours:
                    hours = ", ".join(opening_hours["weekday_text"])
                regular_services.append(
                    f"• {name} - {address}\n• 📞 {phone} | ⏰ {hours}"
                )

        response = ""
        if emergency_services:
            response += "🚨 EMERGÊNCIA 24H\n"
            response += "\n".join(emergency_services)
            response += "\n\n"

        if regular_services:
            response += "🏠 CENTROS DE ATENDIMENTO\n"
            response += "\n".join(regular_services)

        if not response:
            return "Nenhum local de ajuda encontrado com informações suficientes."

        response += "\n\n⚠️ Recomendo confirmar horários e disponibilidade por telefone."
        return response
