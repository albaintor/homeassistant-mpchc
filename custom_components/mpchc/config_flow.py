""" Config Flow for ZidoMedia Players. """
import logging

import aiohttp
import voluptuous as vol
from aiohttp import ClientTimeout, ServerTimeoutError, ClientConnectionError
from aiohttp.web_exceptions import HTTPRequestTimeout

from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from .const import DEFAULT_NAME, DEFAULT_PORT, DOMAIN

DATA_SCHEMA = vol.Schema({vol.Optional(CONF_NAME, default=DEFAULT_NAME, description="Name"): str,
    vol.Required(CONF_HOST, description="Host of MPC-HC"): str,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT, description="Port"): int}
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    try:
        url = f"{data[CONF_HOST]}:{data[CONF_PORT]}"
        if not url.startswith('http://'):
            url = f'http://{url}'
        async with aiohttp.ClientSession() as session:
            response = await session.get(f"{url}/variables.html", timeout=ClientTimeout(3))
    except (ServerTimeoutError, HTTPRequestTimeout, ClientConnectionError):
        raise CannotConnect
    except RuntimeError:
        raise UnknownError

    if response is not None:
        return data

    raise CannotConnect


@config_entries.HANDLERS.register(DOMAIN)
class MPCHCFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """
    ZidooFlowHandler configuration method.

    The schema version of the entries that it creates
    Home Assistant will call your migrate method if the version changes
    (this is not implemented yet)
    """

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize the Zidoo flow."""
        self.discovery_schema = None

    async def async_step_user(self, user_input=None):
        """Manage device specific parameters."""
        errors = {}
        if user_input is not None:
            validated = None
            try:
                validated = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "timeout_error"
            except UnknownError:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if "base" not in errors:
                unique_id = str(f"{DOMAIN}-{validated[CONF_HOST]}")
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                if not user_input[CONF_HOST].startswith('http://'):
                    user_input[CONF_HOST] = f'http://{user_input[CONF_HOST]}'

                return self.async_create_entry(
                    title=DEFAULT_NAME, data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.discovery_schema or DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_import(self, user_input):
        """Handle import."""
        _LOGGER.debug("Import user_info: %s", user_input)
        return await self.async_step_user(user_input)



class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""


class UnknownError(exceptions.HomeAssistantError):
    """Error to indicate there is an unknown error."""
