from __future__ import annotations

from homeassistant.components.sensor import SensorEntity

from homeassistant.const import (
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import Fritz5GCoordinator


SENSORS = [
    ("lte_rsrp", "LTE RSRP", SIGNAL_STRENGTH_DECIBELS_MILLIWATT, None),
    ("lte_rsrq", "LTE RSRQ", "dB", None),
    ("nr_rsrp", "5G NR RSRP", SIGNAL_STRENGTH_DECIBELS_MILLIWATT, None),
    ("nr_rsrq", "5G NR RSRQ", "dB", None),
    ("technology", "Technologie", None, None),
    ("provider", "Provider", None, None),
    ("pci", "PCI", None, None),
    ("distance", "Entfernung", "m", None),
    ("lte_cell_id", "LTE Cell-ID", None, None),
    ("nr_cell_id", "5G Cell-ID", None, None),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    coordinator: Fritz5GCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        Fritz5GSensor(
            coordinator,
            key,
            name,
            unit,
            device_class,
        )
        for key, name, unit, device_class in SENSORS
    )
  
class Fritz5GSensor(CoordinatorEntity, SensorEntity):
    """FRITZ! 5G Sensor."""

    def __init__(
        self,
        coordinator: Fritz5GCoordinator,
        key: str,
        name: str,
        unit: str | None,
        device_class,
    ) -> None:

        super().__init__(coordinator)

        self._key = key

        self._attr_name = name

        self._attr_unique_id = f"{DOMAIN}_{key}"

        self._attr_native_unit_of_measurement = unit

        if device_class is not None:
            self._attr_device_class = device_class

    @property
    def native_value(self):
        """Aktueller Sensorwert."""

        value = self.coordinator.data.get(self._key)

        if value == "":
            return None

        return value

    @property
    def available(self):
        """Sensor verfügbar."""

        return self.coordinator.last_update_success

    @property
    def device_info(self):
        """Geräteinformationen."""

        return {
            "identifiers": {
                (DOMAIN, "fritz_6860_5g")
            },
            "manufacturer": "AVM",
            "model": "FRITZ!Box 6860 5G",
            "name": "FRITZ!Box 6860 5G",
        }

  
