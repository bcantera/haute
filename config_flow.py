"""Config flow for UTE integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .pyute import auth
import aiohttp
import asyncio

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("mail"): str,
        vol.Required("phone"): str,
    }
)


class PlaceholderHub:
    def __init__(self, mail: str) -> None:
        """Initialize."""
        self.mail = mail

    async def check_connection(self, mail: str, phone: str) -> bool:
        """Test if we can connect to the endpoint."""
        try:
            connection = await auth.GetToken.login(mail, phone)
        except aiohttp.client_exceptions.ClientConnectorError:
            return False
        else:
            return True

    async def authenticate(self, mail: str, phone: str) -> bool:
        """Test if we can authenticate with the host."""
        user_login = await auth.GetToken.login(mail, phone)
        if (user_login.status == 401):
            return False
        elif (user_login.status == 200):
            return True

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    hub = PlaceholderHub(data["phone"])

    if not await hub.check_connection(data["mail"], data["phone"]):
        raise CannotConnect

    if not await hub.authenticate(data["mail"], data["phone"]):
        raise InvalidAuth

    return {"title": "Telemedición"}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for UTE."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        # Convert uruguayan phone number to international format
        user_input["phone"] = "598" + user_input["phone"][1:]

        errors = {}

        # Set entity IDs
        await self.async_set_unique_id("ApparentPower")
        await self.async_set_unique_id("MonthlyEnergy")
        self._abort_if_unique_id_configured()

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
