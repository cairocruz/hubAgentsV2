"""
Tests for the PlacesService.
"""
import unittest
from unittest.mock import MagicMock, patch
from services.places_service import PlacesService

class TestPlacesService(unittest.TestCase):
    """
    Test suite for the PlacesService.
    """

    @patch("googlemaps.Client")
    def test_format_places(self, mock_gmaps_client):
        """
        Test that the format_places method correctly formats place data.
        """
        # Mock the Google Maps client
        mock_client_instance = MagicMock()
        mock_gmaps_client.return_value = mock_client_instance

        # Mock the return value of the places and place methods
        mock_client_instance.places.return_value = {
            "results": [
                {"place_id": "emergency_place_id"},
                {"place_id": "regular_place_id"},
            ]
        }
        mock_client_instance.place.side_effect = [
            {
                "result": {
                    "name": "Hospital 24h",
                    "formatted_address": "Rua da Emergência, 123",
                    "formatted_phone_number": "(11) 99999-9999",
                    "opening_hours": {"open_now": True, "periods": [{}]},
                }
            },
            {
                "result": {
                    "name": "Centro de Apoio",
                    "formatted_address": "Av. Acolhimento, 456",
                    "formatted_phone_number": "(11) 88888-8888",
                    "opening_hours": {
                        "weekday_text": ["Segunda a Sexta: 9:00 - 18:00"]
                    },
                }
            },
        ]

        # Initialize the service and call the method
        service = PlacesService(api_key="fake_api_key")
        places = service.find_places("serviço de apoio", "São Paulo, SP")
        formatted_string = service.format_places(places)

        # Assertions
        self.assertIn("🚨 EMERGÊNCIA 24H", formatted_string)
        self.assertIn("Hospital 24h", formatted_string)
        self.assertIn("🏠 CENTROS DE ATENDIMENTO", formatted_string)
        self.assertIn("Centro de Apoio", formatted_string)
        self.assertIn("⚠️ Recomendo confirmar horários", formatted_string)

if __name__ == "__main__":
    unittest.main()
