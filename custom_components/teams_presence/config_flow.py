from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_CLIENT_ID
from homeassistant.core import callback

from .const import DOMAIN, CONF_TENANT_ID, CONF_CLIENT_SECRET

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_TENANT_ID): str,
    vol.Required(CONF_CLIENT_ID): str,
    vol.Required(CONF_CLIENT_SECRET): str,
})


class TeamsPresenceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            from .coordinator import GraphClient

            try:
                client = GraphClient(
                    self.hass,
                    user_input[CONF_TENANT_ID],
                    user_input[CONF_CLIENT_ID],
                    user_input[CONF_CLIENT_SECRET],
                )
                await client.async_get_users()
            except Exception:
                # The exception contains the Microsoft error code/message, but never
                # log the supplied client secret or token.
                _LOGGER.exception(
                    "Microsoft Teams Presence could not validate the Graph connection"
                )
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(
                    f"{user_input[CONF_TENANT_ID]}:{user_input[CONF_CLIENT_ID]}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Microsoft Teams Presence",
                    data=user_input,
                    options={"excluded_users": []},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        # Home Assistant Core 2025.12+ injects config_entry into OptionsFlow.
        return TeamsPresenceOptionsFlow()


class TeamsPresenceOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        from .coordinator import GraphClient

        entry = self.config_entry
        client = GraphClient(
            self.hass,
            entry.data[CONF_TENANT_ID],
            entry.data[CONF_CLIENT_ID],
            entry.data[CONF_CLIENT_SECRET],
        )

        try:
            users = await client.async_get_users()
        except Exception:
            _LOGGER.exception(
                "Unable to retrieve users from Microsoft Graph for the exclusion selector"
            )
            users = []

        users = sorted(users, key=lambda user: (user.get("displayName") or "").lower())
        # Show the same population returned by /users. Do not apply additional
        # userType/accountEnabled filters to this selector.
        options = {
            user["id"]: (
                f'{user.get("displayName") or user.get("userPrincipalName")} — '
                f'{user.get("userPrincipalName", "")}'
            )
            for user in users
            if user.get("id")
        }

        current = entry.options.get("excluded_users", [])
        schema = vol.Schema({
            vol.Optional(
                "excluded_users",
                default=[user_id for user_id in current if user_id in options],
            ): vol.All(vol.Coerce(list), vol.Length(max=len(options)))
        })

        try:
            from homeassistant.helpers.selector import (
                SelectSelector,
                SelectSelectorConfig,
            )

            schema = vol.Schema({
                vol.Optional(
                    "excluded_users",
                    default=[user_id for user_id in current if user_id in options],
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": user_id, "label": label}
                            for user_id, label in options.items()
                        ],
                        multiple=True,
                        mode="list",
                    )
                )
            })
        except (ImportError, TypeError):
            # Keep the voluptuous fallback for Home Assistant versions without
            # this selector configuration.
            pass

        if user_input is not None:
            return self.async_create_entry(
                title="Excluded users",
                data={"excluded_users": user_input.get("excluded_users", [])},
            )

        return self.async_show_form(step_id="init", data_schema=schema)
