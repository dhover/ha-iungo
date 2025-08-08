from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol

from .const import DOMAIN, CONF_HOST, DEFAULT_HOST
from .iungo import async_test_connection, CannotConnect


class IungoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Iungo integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            try:
                can_connect = await async_test_connection(session, user_input[CONF_HOST])
                if not can_connect:
                    errors["base"] = "cannot_connect"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

            if not errors:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_HOST], data=user_input
                )

        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

