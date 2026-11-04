# Changelog

## 0.2.2 — 2026-11-04

- Restore the user-discovery and account-selection behaviour from the working installation: all users returned by Microsoft Graph are included unless manually excluded.
- Remove automatic `userType` and `accountEnabled` filters that could hide valid users.
- Keep user sensors available with state `unknown` when the presence endpoint returns an error, and retry on the next coordinator refresh.
- Add diagnostic logging for user counts, presence counts, authentication errors and Microsoft Graph error codes/messages.
- Keep the Home Assistant Core 2025.12+ Options Flow API and reload the integration when exclusions change.

## 0.2.1 — 2026-11-04

- Prepare the project for public HACS distribution.
- Add HACS metadata, validation workflows and local integration brand assets.
- Update the options flow for Home Assistant Core 2025.12 and newer.
- Reload the integration when excluded-user options change.
- Expand installation, permissions, privacy and troubleshooting documentation.

## 0.2.0

- Initial complete integration package with Microsoft Graph presence polling, automatic user discovery and account exclusions.
