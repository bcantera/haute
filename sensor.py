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

from .pyute import auth, ute, const
from .const import DOMAIN, PLATFORMS
from homeassistant.helpers.aiohttp_client import async_get_clientsession

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    add_entities([CurrentMonthConsumption()])

async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    #session = async_get_clientsession(hass)
    session = await auth.GetToken.login(config["mail"], config["phone"])
#github = GitHubAPI(session, "requester", oauth_token=config[CONF_ACCESS_TOKEN])
    #sensors = [GitHubRepoSensor(github, repo) for repo in config[CONF_REPOS]]
    #async_add_entities([ExampleSensor()])
    async_add_entities([CurrentMonthConsumption()])
    print(const.APP_HEADERS)
#    print(config["phone"])
'''
def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    add_entities([ExampleSensor()])
    add_entities([CurrentMonthConsumption()])
'''
class ExampleSensor(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "UTE Instant power consumption"
    _attr_native_unit_of_measurement = POWER_WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        object1 = ute.ClassA()
        sum = asyncio.run(object1.main())
        self._attr_native_value = sum["wattage"]

class CurrentMonthConsumption(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "UTE Current month consumption"
    _attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        sum2 = asyncio.run(ute.main())
        self._attr_native_value = sum2["current_month_power"]
