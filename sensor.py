"""Platform for sensor integration."""
from __future__ import annotations
from typing_extensions import Self

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import POWER_WATT, ENERGY_KILO_WATT_HOUR
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

import aiohttp
import asyncio

from .const import DOMAIN, PLATFORMS
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .pyute import account, meter

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    add_entities([ApparentPower()])
    add_entities([MonthlyEnergy()])

async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([ApparentPower()])
    async_add_entities([MonthlyEnergy()])

class ApparentPower(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Potencia aparente"
    _attr_native_unit_of_measurement = POWER_WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        user_account = asyncio.run(account.get_user_accounts())
        meter_data = asyncio.run(meter.measures(user_account[-1]))
        self._attr_native_value = meter_data.apparent_power

    @property
    def unique_id(self):
        return "ApparentPower"

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, "Contador UTE")
            },
            "name": "Medidor inteligente",
            "manufacturer": "Kaifa",
            "model": "Monofasico",
            "suggested_area": "Sala contadores",
            "via_device": (DOMAIN, "UTE"),
        }

class MonthlyEnergy(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Energía mensual"
    _attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        user_account = asyncio.run(account.get_user_accounts())
        meter_data = asyncio.run(meter.measures(user_account[-1]))
        self._attr_native_value = meter_data.monthly_consumption

    @property
    def unique_id(self):
        return "MonthlyEnergy"

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, "Contador UTE")
            },
            "name": "Medidor inteligente",
            "manufacturer": "Kaifa",
            "model": "Monofasico",
            "suggested_area": "Sala contadores",
            "via_device": (DOMAIN, "UTE"),
        }
