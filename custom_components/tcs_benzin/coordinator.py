"""Coordinator for TCS Benzinpreis Schweiz."""
from __future__ import annotations

from datetime import timedelta
import logging

import requests

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DOMAIN,
    API_BASE_URL,
    API_STATION_BY_ID,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class TcsBenzinCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch station data from TCS API."""

    def __init__(self, hass: HomeAssistant, station_id: str, scan_interval: int = DEFAULT_SCAN_INTERVAL) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}-{station_id}",
            update_interval=timedelta(minutes=scan_interval),
        )
        self.station_id = station_id
        self.station_name = None
        self._url = f"{API_BASE_URL}/{API_STATION_BY_ID}"

    async def _async_update_data(self) -> dict:
        """Fetch station data from API."""
        return await self.hass.async_add_executor_job(self._fetch_data)

    def _fetch_data(self) -> dict:
        """Fetch station data synchronously."""
        try:
            response = requests.post(
                self._url,
                json={"id": self.station_id},
                headers={"Content-Type": "application/json"},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            # Store basic info
            self.station_name = data.get("displayName", self.station_id)

            # Extract prices
            fuel_collection = data.get("fuelCollection", {})
            prices = {}
            for fuel_type, fuel_data in fuel_collection.items():
                if isinstance(fuel_data, dict) and not fuel_data.get("isDeleted", False):
                    prices[fuel_type] = {
                        "price": fuel_data.get("displayPrice"),
                        "level": fuel_data.get("fiability", {}).get("level"),
                        "levelScore": fuel_data.get("fiability", {}).get("score"),
                        "last_update": fuel_data.get("fiability", {}).get("lastPriceUpdate"),
                        "num_updates": fuel_data.get("fiability", {}).get("numberOfRecentPriceUpdates"),
                    }

            return {
                "id": data.get("id"),
                "name": self.station_name,
                "brand": data.get("brand"),
                "address": data.get("formattedAddress"),
                "location": data.get("location"),
                "prices": prices,
                "has_mastercard_cashback": data.get("hasTCSMastercardCashback", False),
            }

        except requests.exceptions.RequestException as err:
            raise UpdateFailed(f"Error communicating with TCS API: {err}") from err
        except (ValueError, KeyError, TypeError) as err:
            raise UpdateFailed(f"Error parsing TCS API response: {err}") from err
