from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_EXCLUDED_USERS,
    CONF_TENANT_ID,
    DEFAULT_SCAN_INTERVAL,
    GRAPH_BASE,
    STATUS_MAP,
    TOKEN_URL,
)

_LOGGER = logging.getLogger(__name__)


class GraphClient:
    """Small Microsoft Graph client using Home Assistant's shared HTTP session."""

    def __init__(self, hass: HomeAssistant, tenant: str, client_id: str, secret: str):
        self.hass = hass
        self.tenant = tenant
        self.client_id = client_id
        self.secret = secret
        self._session: aiohttp.ClientSession | None = None
        self._token: str | None = None

    async def _session_get(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = async_get_clientsession(self.hass)
        return self._session

    async def async_get_token(self) -> str:
        session = await self._session_get()
        url = TOKEN_URL.format(tenant=self.tenant)
        data = {
            "client_id": self.client_id,
            "client_secret": self.secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }
        async with session.post(url, data=data, timeout=20) as response:
            payload = await response.json(content_type=None)
            if response.status != 200:
                raise UpdateFailed(f"Microsoft identity token request failed: HTTP {response.status}")
            self._token = payload["access_token"]
            return self._token

    async def _request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        session = await self._session_get()
        token = self._token or await self.async_get_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        headers.setdefault("Accept", "application/json")

        async with session.request(
            method, url, headers=headers, timeout=20, **kwargs
        ) as response:
            if response.status == 401:
                token = await self.async_get_token()
                headers["Authorization"] = f"Bearer {token}"
                async with session.request(
                    method, url, headers=headers, timeout=20, **kwargs
                ) as retry:
                    payload = await retry.json(content_type=None)
                    if retry.status >= 400:
                        raise UpdateFailed(
                            f"Microsoft Graph request failed: HTTP {retry.status}"
                        )
                    return payload

            payload = await response.json(content_type=None)
            if response.status >= 400:
                raise UpdateFailed(
                    f"Microsoft Graph request failed: HTTP {response.status}"
                )
            return payload

    async def async_get_users(self) -> list[dict[str, Any]]:
        """Return all users from the Microsoft 365 tenant."""
        users: list[dict[str, Any]] = []
        url = (
            f"{GRAPH_BASE}/users?"
            "$select=id,displayName,givenName,surname,mail,userPrincipalName,userType,accountEnabled"
            "&$top=999"
        )
        while url:
            payload = await self._request("GET", url)
            users.extend(payload.get("value", []))
            url = payload.get("@odata.nextLink")
        return users

    async def async_get_presences(
        self, user_ids: list[str]
    ) -> list[dict[str, Any]]:
        """Return presence information in batches accepted by Microsoft Graph."""
        if not user_ids:
            return []

        result: list[dict[str, Any]] = []
        # Graph's getPresencesByUserId endpoint supports up to 650 IDs per request.
        for start in range(0, len(user_ids), 650):
            chunk = user_ids[start : start + 650]
            payload = await self._request(
                "POST",
                f"{GRAPH_BASE}/communications/getPresencesByUserId",
                headers={"Content-Type": "application/json"},
                json={"ids": chunk},
            )
            result.extend(payload.get("value", []))
        return result


class TeamsPresenceCoordinator(DataUpdateCoordinator):
    """Fetch tenant users and their Teams presence."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.entry = entry
        self.client = GraphClient(
            hass,
            entry.data[CONF_TENANT_ID],
            entry.data[CONF_CLIENT_ID],
            entry.data[CONF_CLIENT_SECRET],
        )
        self.users: dict[str, dict[str, Any]] = {}
        self.presences: dict[str, dict[str, Any]] = {}
        self.excluded = set(entry.options.get(CONF_EXCLUDED_USERS, []))

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name="Microsoft Teams Presence",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            users = await self.client.async_get_users()

            # Only enabled internal Member accounts are monitored.
            # Guest/B2B and disabled accounts are excluded automatically.
            self.users = {
                user["id"]: user
                for user in users
                if (
                    user.get("id")
                    and user["id"] not in self.excluded
                    and user.get("userType", "Member") == "Member"
                    and user.get("accountEnabled", True) is True
                )
            }

            presences = await self.client.async_get_presences(list(self.users))
            self.presences = {
                presence["id"]: presence
                for presence in presences
                if presence.get("id")
            }

            return {
                user_id: {
                    **self.users[user_id],
                    **self.presences.get(user_id, {}),
                    "state": STATUS_MAP.get(
                        self.presences.get(user_id, {}).get("availability"),
                        "unknown",
                    ),
                }
                for user_id in self.users
            }
        except Exception as err:
            raise UpdateFailed(str(err)) from err
