"""Config flow for TCS Benzinpreis Schweiz."""
from __future__ import annotations

import logging
import re
from typing import Any

import requests

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_STATION_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    API_BASE_URL,
    API_STATION_BY_ID,
)

import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

# Station ID from URL: e.g., "zpIcUjj4Ct2id9PXp2Wp" from ".../station/zpIcUjj4Ct2id9PXp2Wp/SP95"
STATION_ID_PATTERN = re.compile(r"([A-Za-z0-9_-]{20,30})")


def extract_station_id(user_input: str) -> str | None:
    """Extract station ID from a URL or raw ID."""
    user_input = user_input.strip().rstrip("/")
    # If it looks like a URL, extract the ID
    if "/station/" in user_input:
        match = re.search(r"/station/([A-Za-z0-9_-]+)", user_input)
        if match:
            return match.group(1)
    # Try direct match
    match = STATION_ID_PATTERN.match(user_input)
    if match:
        return match.group(1)
    return None


def validate_station(station_id: str) -> dict | None:
    """Validate and fetch station data."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/{API_STATION_BY_ID}",
            json={"id": station_id},
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("id"):
            return data
    except (requests.RequestException, ValueError):
        pass
    return None


class TcsBenzinConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TCS Benzinpreis Schweiz."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            station_id = extract_station_id(user_input[CONF_STATION_ID])
            if not station_id:
                errors[CONF_STATION_ID] = "invalid_station_id"
            else:
                # Check if already configured
                await self.async_set_unique_id(station_id)
                self._abort_if_unique_id_configured()

                # Validate station
                station_data = await self.hass.async_add_executor_job(
                    validate_station, station_id
                )
                if station_data is None:
                    errors[CONF_STATION_ID] = "cannot_connect"
                else:
                    scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                    return self.async_create_entry(
                        title=station_data.get("displayName", station_id),
                        data={
                            CONF_STATION_ID: station_id,
                            CONF_SCAN_INTERVAL: scan_interval,
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_STATION_ID): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL,
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=1440)),
                }
            ),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return TcsBenzinOptionsFlow(config_entry)


class TcsBenzinOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.data.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=1440)),
                }
            ),
        )
