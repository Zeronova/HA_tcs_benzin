"""Sensor platform for TCS Benzinpreis Schweiz."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, FUEL_TYPES, FUEL_ICONS, FIABILITY_LEVELS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TCS Benzin sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    station_id = entry.data.get("station_id")

    entities: list = []

    # Fuel price sensors
    for fuel_type in FUEL_TYPES:
        if fuel_type in coordinator.data.get("prices", {}):
            entities.append(
                TcsBenzinSensor(coordinator, station_id, fuel_type)
            )

    # Station metadata sensors (created once per station)
    entities.append(TcsBenzinBrandSensor(coordinator, station_id))
    entities.append(TcsBenzinAddressSensor(coordinator, station_id))

    if entities:
        async_add_entities(entities)


class TcsBenzinSensor(CoordinatorEntity, SensorEntity):
    """Representation of a fuel price sensor."""

    def __init__(self, coordinator, station_id: str, fuel_type: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._station_id = station_id
        self._fuel_type = fuel_type
        self._attr_name = f"{FUEL_TYPES.get(fuel_type, fuel_type)}"
        self._attr_unique_id = f"{station_id}_{fuel_type}"
        self._attr_unit_of_measurement = "CHF/l"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = FUEL_ICONS.get(fuel_type, "mdi:gas-station")
        self._attr_entity_registry_enabled_default = True

    @property
    def device_info(self) -> dict:
        """Return device info."""
        data = self.coordinator.data
        return {
            "identifiers": {(DOMAIN, self._station_id)},
            "name": data.get("name", f"Tankstelle {self._station_id}"),
            "manufacturer": data.get("brand", "TCS"),
            "model": "Tankstelle",
            "sw_version": "v0.1.0",
            "configuration_url": f"https://benzin.tcs.ch/de/station/{self._station_id}",
        }

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        prices = self.coordinator.data.get("prices", {})
        fuel_data = prices.get(self._fuel_type)
        if fuel_data:
            return fuel_data.get("price")
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        prices = self.coordinator.data.get("prices", {})
        fuel_data = prices.get(self._fuel_type, {})

        attrs = {
            "station_id": self._station_id,
            "fuel_type": self._fuel_type,
            "fuel_type_display": FUEL_TYPES.get(self._fuel_type, self._fuel_type),
            "brand": self.coordinator.data.get("brand"),
            "address": self.coordinator.data.get("address"),
        }

        # Fiability info
        level = fuel_data.get("level")
        if level:
            attrs["fiability_level"] = level
            attrs["fiability_label"] = FIABILITY_LEVELS.get(level, level)
            attrs["fiability_score"] = fuel_data.get("levelScore")

        # Last update
        last_update = fuel_data.get("last_update")
        if last_update:
            import datetime
            seconds = last_update.get("_seconds")
            if seconds:
                attrs["last_price_update"] = datetime.datetime.fromtimestamp(
                    seconds, tz=datetime.timezone.utc
                ).isoformat()

        # Number of recent updates
        num_updates = fuel_data.get("num_updates")
        if num_updates is not None:
            attrs["num_recent_price_updates"] = num_updates

        return attrs


class TcsBenzinBrandSensor(CoordinatorEntity, SensorEntity):
    """Brand of the gas station with logo."""

    def __init__(self, coordinator, station_id: str) -> None:
        """Initialize the brand sensor."""
        super().__init__(coordinator)
        self._station_id = station_id
        self._attr_name = "Marke"
        self._attr_unique_id = f"{station_id}_brand"
        self._attr_icon = "mdi:storefront-outline"
        self._attr_entity_registry_enabled_default = True

    @property
    def device_info(self) -> dict:
        """Return device info."""
        data = self.coordinator.data
        return {
            "identifiers": {(DOMAIN, self._station_id)},
            "name": data.get("name", f"Tankstelle {self._station_id}"),
            "manufacturer": data.get("brand", "TCS"),
            "model": "Tankstelle",
            "sw_version": "v0.1.0",
            "configuration_url": f"https://benzin.tcs.ch/de/station/{self._station_id}",
        }

    @property
    def native_value(self) -> str | None:
        """Return the brand name."""
        return self.coordinator.data.get("brand") or "Unbekannt"

    @property
    def entity_picture(self) -> str | None:
        """Return the brand logo URL."""
        brand = self.coordinator.data.get("brand")
        if brand:
            return f"https://benzin.tcs.ch/images/brands/icons/{brand.lower()}.webp"
        return None


class TcsBenzinAddressSensor(CoordinatorEntity, SensorEntity):
    """Address of the gas station."""

    def __init__(self, coordinator, station_id: str) -> None:
        """Initialize the address sensor."""
        super().__init__(coordinator)
        self._station_id = station_id
        self._attr_name = "Adresse"
        self._attr_unique_id = f"{station_id}_address"
        self._attr_icon = "mdi:map-marker"
        self._attr_entity_registry_enabled_default = True

    @property
    def device_info(self) -> dict:
        """Return device info."""
        data = self.coordinator.data
        return {
            "identifiers": {(DOMAIN, self._station_id)},
            "name": data.get("name", f"Tankstelle {self._station_id}"),
            "manufacturer": data.get("brand", "TCS"),
            "model": "Tankstelle",
            "sw_version": "v0.1.0",
            "configuration_url": f"https://benzin.tcs.ch/de/station/{self._station_id}",
        }

    @property
    def native_value(self) -> str | None:
        """Return the address."""
        return self.coordinator.data.get("address") or "Unbekannt"
