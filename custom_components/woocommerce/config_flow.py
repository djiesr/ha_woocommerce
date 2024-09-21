from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class WooCommerceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WooCommerce."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        return self.async_show_form(
            step_id="user", 
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("consumer_key"): str,
                vol.Required("consumer_secret"): str,
                vol.Required("url"): str,
            })
        )
