from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_VIN, DOMAIN, SENSOR_TYPES
from .coordinator import DucatiLinkCoordinator

_TELEMETRY_KEY_MAP = {
    "odometer": "odometer",
    "mileage": "odometer",
    "fuel_level": "fuel_level",
    "fuelLevel": "fuel_level",
    "battery_voltage": "battery_voltage",
    "batteryVoltage": "battery_voltage",
    "next_service_km": "next_service_km",
    "nextServiceKm": "next_service_km",
    "next_service_date": "next_service_date",
    "nextServiceDate": "next_service_date",
    "last_update": "last_update",
    "lastUpdate": "last_update",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: DucatiLinkCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        DucatiLinkSensor(coordinator, entry, sensor_key)
        for sensor_key in SENSOR_TYPES
    ]
    async_add_entities(entities)


class DucatiLinkSensor(CoordinatorEntity[DucatiLinkCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DucatiLinkCoordinator,
        entry: ConfigEntry,
        sensor_key: str,
    ) -> None:
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._vin: str = entry.data[CONF_VIN]
        spec = SENSOR_TYPES[sensor_key]

        self._attr_unique_id = f"{self._vin}_{sensor_key}"
        self._attr_name = spec["name"]
        self._attr_native_unit_of_measurement = spec["unit"]
        self._attr_icon = spec["icon"]

        if spec["device_class"]:
            self._attr_device_class = SensorDeviceClass(spec["device_class"])
        if spec["state_class"]:
            self._attr_state_class = SensorStateClass(spec["state_class"])

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._vin)},
            name=f"Ducati ({self._vin[-6:]})",
            manufacturer="Ducati",
            model=coordinator.data.get("model") if coordinator.data else None,
            serial_number=self._vin,
        )

    @property
    def native_value(self) -> Any:
        if not self.coordinator.data:
            return None
        data = self.coordinator.data
        # Try camelCase and snake_case variants
        for raw_key, mapped in _TELEMETRY_KEY_MAP.items():
            if mapped == self._sensor_key and raw_key in data:
                return data[raw_key]
        return data.get(self._sensor_key)
