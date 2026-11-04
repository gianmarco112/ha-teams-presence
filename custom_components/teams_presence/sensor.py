from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_ACTIVITY,
    ATTR_AVAILABILITY,
    ATTR_DISPLAY_NAME,
    ATTR_EMAIL,
    ATTR_USER_ID,
    DOMAIN,
)
from .coordinator import TeamsPresenceCoordinator


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up one sensor for every monitored Microsoft 365 user."""
    coordinator: TeamsPresenceCoordinator = hass.data[DOMAIN][entry.entry_id]
    known = set()

    def add_current():
        entities = []
        for user_id in coordinator.data:
            if user_id in known:
                continue
            entities.append(TeamsPresenceSensor(coordinator, user_id))
            known.add(user_id)
        if entities:
            async_add_entities(entities)

    add_current()

    def coordinator_updated():
        add_current()

    remove_listener = coordinator.async_add_listener(coordinator_updated)
    entry.async_on_unload(remove_listener)


class TeamsPresenceSensor(CoordinatorEntity, SensorEntity):
    """Represent one user's Teams presence."""

    _attr_should_poll = False

    def __init__(self, coordinator, user_id):
        super().__init__(coordinator)
        self.user_id = user_id

        data = coordinator.data.get(user_id, {})
        name = data.get("displayName") or data.get("userPrincipalName") or user_id
        self._attr_name = f"Teams {name}"
        self._attr_unique_id = f"teams_presence_{user_id}"
        self._attr_icon = "mdi:microsoft-teams"

    @property
    def native_value(self):
        data = self.coordinator.data.get(self.user_id, {})
        return data.get("state", "unknown")

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get(self.user_id, {})
        return {
            ATTR_USER_ID: self.user_id,
            ATTR_DISPLAY_NAME: data.get("displayName"),
            ATTR_EMAIL: data.get("mail") or data.get("userPrincipalName"),
            ATTR_AVAILABILITY: data.get("availability"),
            ATTR_ACTIVITY: data.get("activity"),
        }

    @property
    def available(self):
        return self.user_id in self.coordinator.data
