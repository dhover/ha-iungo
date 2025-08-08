import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import IungoDataUpdateCoordinator

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass, config):
    """Set up the iungo integration."""
    return True

async def async_setup_entry(hass, entry):
    """Set up a config entry for iungo."""

    coordinator = IungoDataUpdateCoordinator(hass, entry)
    await coordinator.async_initialize()  # Fetch object_info once at startup
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault("iungo", {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "update"])
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, ["sensor", "update"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok