"""Support to interface with the MPC-HC Web API."""
import datetime
import datetime as dt
import logging
import re

import requests
import voluptuous as vol

from homeassistant.components.media_player import PLATFORM_SCHEMA, MediaPlayerEntity, MediaType, MediaPlayerState
from homeassistant.components.media_player.const import (
    MediaPlayerEntityFeature,
    MEDIA_TYPE_VIDEO
)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
)
import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "MPC-HC"
DEFAULT_PORT = 13579

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


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the MPC-HC platform."""
    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)

    url = f"{host}:{port}"
    _LOGGER.info("Configure MPCHC device %s : %s", name, url);
    add_entities([MpcHcDevice(name, url)], True)


class MpcHcDevice(MediaPlayerEntity):
    """Representation of a MPC-HC server."""

    def __init__(self, name, url):
        """Initialize the MPC-HC device."""
        self._name = name
        self._url = url
        self._player_variables = {}
        self._available = False
        self._media_duration = None
        self._media_position = None
        self._media_last_updated = None
        self._media_type = MEDIA_TYPE_VIDEO
        self._media_title = None
        self._media_state = MediaPlayerState.OFF

    def update(self):
        """Get the latest details."""
        try:
            _LOGGER.debug("MPC udpate : %s", self._url)
            response = requests.get(f"{self._url}/variables.html", data=None, timeout=3)
            response.encoding = response.apparent_encoding

            mpchc_variables = re.findall(r'<p id="(.+?)">(.+?)</p>', response.text)

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
                    self._media_title = self._media_title.rsplit( ".",  1)[0]
            except Exception:
                pass
            self._available = True
        except requests.exceptions.RequestException as exr:
            _LOGGER.error("MPC error %s", exr)
            if self.available:
                _LOGGER.error("Could not connect to MPC-HC at: %s", self._url)

            self._player_variables = {}
            self._available = False
        except Exception as ex:
            _LOGGER.error("MPC error %s", ex)

    def _send_command(self, command_id):
        """Send a command to MPC-HC via its window message ID."""
        try:
            params = {"wm_command": command_id}
            requests.get(f"{self._url}/command.html", params=params, timeout=3)
        except requests.exceptions.RequestException:
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

    def turn_off(self) -> None:
        """Send quit command."""
        self._send_command(816)

    def media_seek(self, position: float) -> None:
        try:
            params = {"wm_command": -1, "position": str(datetime.timedelta(seconds=position))}
            requests.post(f"{self._url}/command.html", params=params, timeout=3)
            self.update()
            self.schedule_update_ha_state()
        except requests.exceptions.RequestException:
            _LOGGER.error(
                "Could not send command %d to MPC-HC at: %s", -1, self._url
            )

    def volume_up(self):
        """Volume up the media player."""
        self._send_command(907)

    def volume_down(self):
        """Volume down media player."""
        self._send_command(908)

    def mute_volume(self, mute):
        """Mute the volume."""
        self._send_command(909)

    def media_play(self):
        """Send play command."""
        self._send_command(887)

    def media_pause(self):
        """Send pause command."""
        self._send_command(888)

    def media_stop(self):
        """Send stop command."""
        self._send_command(890)

    def media_next_track(self):
        """Send next track command."""
        self._send_command(920)

    def media_previous_track(self):
        """Send previous track command."""
        self._send_command(919)
