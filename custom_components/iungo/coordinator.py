from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import CONF_HOST, DEFAULT_UPDATE_INTERVAL
from .iungo import async_get_object_info, async_get_object_values, parse_object_values
from datetime import timedelta
import logging

_LOGGER = logging.getLogger(__name__)

class IungoDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, update_interval=None):
        update_interval = update_interval or timedelta(seconds=DEFAULT_UPDATE_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name="iungo",
            update_interval=update_interval,
        )
        self.entry = entry

    async def _async_update_data(self):
        host = self.entry.data.get(CONF_HOST)
        if not host:
            _LOGGER.error("No host configured for Iungo integration")
            return {}

        session = self.hass.helpers.aiohttp_client.async_get_clientsession(self.hass)
        object_info = await async_get_object_info(session, host)
        raw_object_values = await async_get_object_values(session, host)
        object_values = parse_object_values(raw_object_values)
        return {
            "object_info": object_info,
            "object_values": object_values,
        }