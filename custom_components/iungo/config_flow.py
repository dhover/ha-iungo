from homeassistant import config_entries
from .const import DOMAIN, CONF_HOST
import voluptuous as vol

class IungoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Iungo."""

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_import(self, import_info):
        """Import a config entry from YAML."""
        return self.async_create_entry(title="Iungo", data=import_info)