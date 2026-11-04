from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_CLIENT_ID
from homeassistant.core import callback

from .const import DOMAIN, CONF_TENANT_ID, CONF_CLIENT_SECRET

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
        # Current Home Assistant injects the config entry into OptionsFlow.
        # Do not pass it to __init__ or assign self.config_entry manually.
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
            users = []

        users = sorted(users, key=lambda u: (u.get("displayName") or "").lower())
        options = {
            u["id"]: f'{u.get("displayName") or u.get("userPrincipalName")} — {u.get("userPrincipalName", "")}'
            for u in users
            if (
                u.get("id")
                and u.get("userType", "Member") == "Member"
                and u.get("accountEnabled", True) is True
            )
        }

        current = entry.options.get("excluded_users", [])

        schema = vol.Schema({
            vol.Optional(
                "excluded_users",
                default=[x for x in current if x in options],
            ): vol.All(vol.Coerce(list), vol.Length(max=len(options)))
        })

        # Replace the generic list coercion with a multi-select selector when available.
        try:
            from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig
            schema = vol.Schema({
                vol.Optional(
                    "excluded_users",
                    default=[x for x in current if x in options],
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": uid, "label": label}
                            for uid, label in options.items()
                        ],
                        multiple=True,
                        mode="list",
                    )
                )
            })
        except Exception:
            pass

        if user_input is not None:
            return self.async_create_entry(
                title="Excluded users",
                data={"excluded_users": user_input.get("excluded_users", [])},
            )

        return self.async_show_form(step_id="init", data_schema=schema)
