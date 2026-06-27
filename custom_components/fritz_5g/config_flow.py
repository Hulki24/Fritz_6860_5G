from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD

from .const import DOMAIN


class Fritz5GConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """FRITZ! 5G Config Flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):

        errors = {}

        if user_input is not None:

            return self.async_create_entry(
                title=user_input[CONF_HOST],
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="fritz.box"): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
