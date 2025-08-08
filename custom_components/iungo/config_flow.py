
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_HOST, DEFAULT_UPDATE_INTERVAL
from .iungo import (
    IungoError,
    async_get_object_info,
    async_get_object_values,
    parse_object_values,
    async_get_sysinfo,
    async_get_hwinfo,
    async_get_latest_version
)

_LOGGER = logging.getLogger(__name__)


class IungoDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_data",
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
        )
        self.entry = entry
        self.object_info = None

    async def async_initialize(self):
        host = self.entry.data.get(CONF_HOST)
        if not host:
            raise ConfigEntryNotReady("No host configured for Iungo integration")

        session = async_get_clientsession(self.hass)
        try:
            self.object_info = await async_get_object_info(session, host)
        except IungoError as err:
            raise ConfigEntryNotReady from err
