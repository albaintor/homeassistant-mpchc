"""Remote control support for Android TV Remote."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import aiohttp

from aiohttp import ClientTimeout, ServerTimeoutError, ClientConnectionError
from aiohttp.web_exceptions import HTTPRequestTimeout
from homeassistant.components.remote import (
    ATTR_DELAY_SECS,
    ATTR_NUM_REPEATS,
    DEFAULT_DELAY_SECS,
    DEFAULT_NUM_REPEATS,
    RemoteEntity,
    PLATFORM_SCHEMA, ENTITY_ID_FORMAT, RemoteEntityFeature
)
from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
)

import homeassistant.helpers.config_validation as cv

import voluptuous as vol

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import MPCHC_COMMANDS, DOMAIN

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "MPC-HC"
DEFAULT_PORT = 13579

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the MPC-HC platform."""
    _LOGGER.info("Configure MPCHC device %s : %s", config)
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=config
        )
    )


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Media Player from a config entry."""
    async_add_entities([MPCHCRemote(config_entry)])


class MPCHCRemote(RemoteEntity):
    """Android TV Remote Entity."""

    _attr_supported_features = RemoteEntityFeature.ACTIVITY

    def __init__(self, config_entry: ConfigEntry):
        """Initialize the MPC-HC device."""
        self._name = config_entry.data[CONF_NAME]
        self._url = f'{config_entry.data[CONF_HOST]}:{config_entry.data[CONF_PORT]}'
        self._available = True
        self._session = aiohttp.ClientSession()
        entity_name = self._url.lstrip('http://')
        self._unique_id = ENTITY_ID_FORMAT.format(
            f"{entity_name}_remote")

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Mac address is unique identifiers within a specific domain
                (DOMAIN, self._url)
            },
            name=self._name,
            manufacturer=DEFAULT_NAME,
            model=""
        )

    @property
    def unique_id(self) -> str | None:
        return self._unique_id

    @property
    def supported_features(self) -> RemoteEntityFeature:
        return self._attr_supported_features

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send commands to one device."""
        num_repeats = kwargs.get(ATTR_NUM_REPEATS, DEFAULT_NUM_REPEATS)
        delay_secs = kwargs.get(ATTR_DELAY_SECS, DEFAULT_DELAY_SECS)
        # hold_secs = kwargs.get(ATTR_HOLD_SECS, DEFAULT_HOLD_SECS)

        _LOGGER.debug("async_send_command %s %d repeats %d delay", ''.join(list(command)), num_repeats, delay_secs)

        for _ in range(num_repeats):
            for single_command in command:
                single_command = MPCHC_COMMANDS.get(single_command, single_command)
                _LOGGER.debug("Remote command %", single_command)
                try:
                    params = {"wm_command": single_command}
                    await self._session.get(f"{self._url}/command.html", params=params, timeout=ClientTimeout(3))
                except (ServerTimeoutError, HTTPRequestTimeout, ClientConnectionError):
                    _LOGGER.error(
                        "Could not send command %d to MPC-HC at: %s", single_command, self._url
                    )
