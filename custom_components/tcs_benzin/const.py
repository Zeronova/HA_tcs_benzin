"""Constants for TCS Benzinpreis Schweiz."""
from homeassistant.const import Platform

DOMAIN = "tcs_benzin"
PLATFORMS = [Platform.SENSOR]

# API
API_BASE_URL = "https://europe-west6-tcs-digitalbackend.cloudfunctions.net"
API_STATION_BY_ID = "benzinGetStationById"

# Defaults
DEFAULT_SCAN_INTERVAL = 30  # minutes
DEFAULT_NAME = "TCS Benzinpreis"

# Fuel type aliases (internal_key -> display name)
FUEL_TYPES = {
    "SP95": "Bleifrei 95",
    "SP98": "Bleifrei 98+",
    "DIESEL": "Diesel",
    "DIESEL_PREMIUM": "Premium-Diesel",
    "GPL": "LPG",
    "ADBLUE": "Adblue",
    "CNG": "Erdgas",
    "E85": "Ethanol 85",
    "HVO100": "HVO100",
    "H2": "Wasserstoff",
}

# Fuel type icons
FUEL_ICONS = {
    "SP95": "mdi:gas-station",
    "SP98": "mdi:gas-station",
    "DIESEL": "mdi:gas-station",
    "DIESEL_PREMIUM": "mdi:gas-station",
    "GPL": "mdi:propane-tank",
    "ADBLUE": "mdi:chemical-weapon",
    "CNG": "mdi:fire",
    "E85": "mdi:gas-station",
    "HVO100": "mdi:gas-station",
    "H2": "mdi:water",
}

# Fiability levels
FIABILITY_LEVELS = {
    "CONFIDENT": "Zuverlässig",
    "MODERATE": "Mittel",
    "LOW": "Niedrig",
    "OLD_LAST_UPDATE": "Alte Daten",
}

# Config flow
CONF_STATION_ID = "station_id"
CONF_SCAN_INTERVAL = "scan_interval"
