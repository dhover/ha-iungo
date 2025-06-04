from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from .const import DOMAIN, CONF_HOST

class IungoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Iungo integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Prevent duplicate entries for the same host
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_HOST],
                data=user_input,
            )

        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return IungoOptionsFlowHandler(config_entry)

class IungoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Iungo."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return self.async_create_entry(title="", data={})