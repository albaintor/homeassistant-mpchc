"""Support to interface with the MPC-HC Web API."""
import datetime
import datetime as dt
import logging
import re

import aiohttp
import voluptuous as vol
from aiohttp import ClientTimeout, ServerTimeoutError, ClientConnectionError
from aiohttp.web_exceptions import HTTPRequestTimeout

from homeassistant.components.media_player import PLATFORM_SCHEMA, MediaPlayerEntity, MediaType, MediaPlayerState, \
    ENTITY_ID_FORMAT
from homeassistant.components.media_player.const import (
    MediaPlayerEntityFeature,
    MEDIA_TYPE_VIDEO
)
from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
)
import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_NAME, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

SUPPORT_MPCHC = (
        MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.SEEK
    #| MediaPlayerEntityFeature.BROWSE_MEDIA TODO
)

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
    async_add_entities([MpcHcDevice(config_entry)])


class MpcHcDevice(MediaPlayerEntity):
    """Representation of a MPC-HC server."""

    def __init__(self, config_entry: ConfigEntry):
        """Initialize the MPC-HC device."""
        self._name = config_entry.data[CONF_NAME]
        self._url = f'{config_entry.data[CONF_HOST]}:{config_entry.data[CONF_PORT]}'
        self._player_variables = {}
        self._available = False
        self._media_duration = None
        self._media_position = None
        self._media_last_updated = None
        self._media_type = MEDIA_TYPE_VIDEO
        self._media_title = None
        self._media_state = MediaPlayerState.OFF
        self._session = aiohttp.ClientSession()
        entity_name = self._url.lstrip('http://')
        self._unique_id = ENTITY_ID_FORMAT.format(
            f"{entity_name}_media_player")

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

    async def async_update(self):
        """Get the latest details."""
        try:
            _LOGGER.debug("MPC udpate : %s", self._url)
            response = await self._session.get(f"{self._url}/variables.html", timeout=ClientTimeout(3))
            mpchc_variables = re.findall(r'<p id="(.+?)">(.+?)</p>', await response.text(encoding="utf-8"))

            _LOGGER.debug("MPC data %s", mpchc_variables)
            for var in mpchc_variables:
                self._player_variables[var[0]] = var[1].lower()

            state = self._player_variables.get("state", None)
            if state is None:
                self._media_state = MediaPlayerState.OFF
            elif state == "2":
                self._media_state = MediaPlayerState.PLAYING
            elif state == "1":
                self._media_state = MediaPlayerState.PAUSED
            else:
                self._media_state = MediaPlayerState.IDLE
            try:
                self._media_last_updated = dt_util.utcnow()
                duration = self._player_variables.get("durationstring", "00:00:00").split(":")
                self._media_duration = int(duration[0]) * 3600 + int(duration[1]) * 60 + int(duration[2])
                position = self._player_variables.get("positionstring", "00:00:00").split(":")
                self._media_position = int(position[0]) * 3600 + int(position[1]) * 60 + int(position[2])
                self._media_title = self._player_variables.get("file", None)
                if self._media_title:
                    self._media_title = self._media_title.rsplit(".", 1)[0]
            except Exception as ex:
                pass
            self._available = True
        except (ServerTimeoutError, HTTPRequestTimeout, ClientConnectionError) as exr:
            _LOGGER.debug("MPC error %s", exr)
            if self.available:
                _LOGGER.error("Could not connect to MPC-HC at: %s", self._url)

            self._player_variables = {}
            self._available = False
        except Exception as ex:
            _LOGGER.error("MPC error %s", ex)

    async def _send_command(self, command_id):
        """Send a command to MPC-HC via its window message ID."""
        try:
            params = {"wm_command": command_id}
            _LOGGER.debug("Send command %s %s", f"{self._url}/command.html", params)
            await self._session.get(f"{self._url}/command.html", params=params, timeout=ClientTimeout(3))
        except (ServerTimeoutError, HTTPRequestTimeout, ClientConnectionError):
            _LOGGER.error(
                "Could not send command %d to MPC-HC at: %s", command_id, self._url
            )

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the state of the device."""
        return self._media_state

    @property
    def media_content_type(self) -> MediaType | str | None:
        return self._media_type

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    @property
    def media_title(self):
        """Return the title of current playing media."""
        return self._media_title

    @property
    def volume_level(self):
        """Return the volume level of the media player (0..1)."""
        return int(self._player_variables.get("volumelevel", 0)) / 100.0

    @property
    def is_volume_muted(self):
        """Return boolean if volume is currently muted."""
        return self._player_variables.get("muted", "0") == "1"

    @property
    def media_duration(self) -> int | None:
        """Return the duration of the current playing media in seconds."""
        return self._media_duration

    @property
    def media_position(self) -> int | None:
        """Return the position of the current playing media in seconds."""
        return self._media_position

    @property
    def media_position_updated_at(self) -> dt.datetime | None:
        return self._media_last_updated

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_MPCHC

    async def async_turn_off(self) -> None:
        """Send quit command."""
        await self._send_command(816)

    async def async_media_seek(self, position: float) -> None:
        try:
            params = {"wm_command": -1, "position": str(datetime.timedelta(seconds=position))}
            await self._session.post(f"{self._url}/command.html", params=params, timeout=ClientTimeout(3))
            await self.async_update()
            self.async_schedule_update_ha_state()
        except (ServerTimeoutError, HTTPRequestTimeout, ClientConnectionError):
            _LOGGER.error(
                "Could not send command %d to MPC-HC at: %s", -1, self._url
            )

    async def async_volume_up(self):
        """Volume up the media player."""
        await self._send_command(907)

    async def async_volume_down(self):
        """Volume down media player."""
        await self._send_command(908)

    async def async_mute_volume(self, mute):
        """Mute the volume."""
        await self._send_command(909)

    async def async_media_play(self):
        """Send play command."""
        await self._send_command(887)

    async def async_media_play_pause(self):
        """Send play/pause command."""
        await self._send_command(888)

    async def async_media_pause(self):
        """Send pause command."""
        await self._send_command(888)

    async def async_media_stop(self):
        """Send stop command."""
        await self._send_command(890)

    async def async_media_next_track(self):
        """Send next track command."""
        await self._send_command(920)

    async def async_media_previous_track(self):
        """Send previous track command."""
        await self._send_command(919)
