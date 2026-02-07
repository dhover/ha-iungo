"""Data coordinators for the iungo integration."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_HOST, DEFAULT_UPDATE_INTERVAL, DEFAULT_FIRMWARE_UPDATE_INTERVAL
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
    """Data update coordinator for Iungo data."""

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
        """Initialize the coordinator by fetching object info."""

        host = self.entry.data.get(CONF_HOST)
        if not host:
            raise ConfigEntryNotReady(
                "No host configured for Iungo integration")

        session = async_get_clientsession(self.hass)
        try:
            self.object_info = await async_get_object_info(session, host)
        except IungoError as err:
            raise ConfigEntryNotReady from err

    async def _async_update_data(self):
        """Fetch data from the Iungo API."""

        host = self.entry.data.get(CONF_HOST)
        if not host:
            raise UpdateFailed("No host configured for Iungo integration")

        session = async_get_clientsession(self.hass)
        try:
            if self.object_info is None:
                await self.async_initialize()
            raw_object_values = await async_get_object_values(session, host)
            object_values = parse_object_values(raw_object_values)
            return {
                "object_info": self.object_info,
                "object_values": object_values,
            }
        except IungoError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


class IungoFirmwareUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Iungo firmware info."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_firmware",
            update_interval=timedelta(
                seconds=DEFAULT_FIRMWARE_UPDATE_INTERVAL),
        )
        self.entry = entry

    async def _async_update_data(self):
        """Fetch firmware info from the Iungo API."""

        host = self.entry.data.get(CONF_HOST)
        if not host:
            raise UpdateFailed("No host configured for Iungo integration")

        session = async_get_clientsession(self.hass)
        try:
            sysinfo = await async_get_sysinfo(session, host)
            hwinfo = await async_get_hwinfo(session, host)
            latest_version = await async_get_latest_version(session, host)
            return {
                "sysinfo": sysinfo,
                "hwinfo": hwinfo,
                "latest_version": latest_version,
            }
        except IungoError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
