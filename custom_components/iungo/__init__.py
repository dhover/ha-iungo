from .const import DOMAIN

async def async_setup(hass, config):
    """Set up the iungo integration."""
    return True

async def async_setup_entry(hass, entry):
    """Set up a config entry for iungo."""
    from .coordinator import IungoDataUpdateCoordinator

    coordinator = IungoDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    return True