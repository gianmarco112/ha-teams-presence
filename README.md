<div align="center">

# Microsoft Teams Presence

![Microsoft Teams Presence](custom_components/teams_presence/brand/logo.svg)

### Bring Microsoft Teams presence into Home Assistant.

Monitor Microsoft 365 availability through Microsoft Graph and expose each selected colleague as a Home Assistant sensor.

[![HACS](https://img.shields.io/badge/HACS-Custom%20Integration-41BDF5?logo=homeassistantcommunitystore&logoColor=white)](https://www.hacs.xyz/)
[![Validate](https://github.com/gianmarco112/ha-teams-presence/actions/workflows/validate.yaml/badge.svg)](https://github.com/gianmarco112/ha-teams-presence/actions/workflows/validate.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.2.2-blue.svg)](https://github.com/gianmarco112/ha-teams-presence/releases)

[Install with HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=gianmarco112&repository=ha-teams-presence&category=integration) · [Report a bug](https://github.com/gianmarco112/ha-teams-presence/issues) · [Request a feature](https://github.com/gianmarco112/ha-teams-presence/issues/new/choose)

</div>

---

## Overview

**Microsoft Teams Presence** is a custom integration for [Home Assistant](https://www.home-assistant.io/) that reads presence information from Microsoft Graph. It discovers users returned by Microsoft Graph in your Microsoft 365 tenant and creates one sensor for each monitored account.

It is designed for personal dashboards, office presence panels and automations. It is not an official Microsoft or Home Assistant integration.

## Features

| Feature | Description |
|---|---|
| Microsoft Entra ID | Secure app-only authentication using the OAuth 2.0 client credentials flow |
| Automatic discovery | Finds users in your tenant through Microsoft Graph |
| Presence sensors | Creates one sensor for every monitored user |
| User exclusions | Excludes accounts selected manually in the integration options |
| User exclusions | Select additional accounts to exclude in the integration options |
| Periodic refresh | Refreshes presence data periodically (default: 60 seconds) |
| UI configuration | Configure credentials and exclusions from Home Assistant; no YAML editing required |
| Localization | English and Italian translations |

## Requirements

- Home Assistant Core **2025.12.0 or newer** (the integration uses the current Options Flow API).
- HACS installed and configured.
- A Microsoft 365 tenant where you are authorized to register an application.
- An administrator who can grant Microsoft Graph **Application permissions** and admin consent.

### Microsoft Graph permissions

The app registration requires these **Application** permissions:

| Permission | Purpose |
|---|---|
| `User.Read.All` | Discover users in the Microsoft 365 tenant |
| `Presence.Read.All` | Read Teams presence for users in the tenant |

Grant **admin consent** after adding both permissions. The integration requests an app-only access token using `https://graph.microsoft.com/.default`.

> **Least privilege:** These permissions are tenant-wide application permissions. Review them with your Microsoft 365 / Entra administrator and use a dedicated app registration. Do not grant them in a tenant where you do not have explicit authorization.

## Installation

### Recommended: HACS custom repository

1. Make sure [HACS](https://www.hacs.xyz/docs/use/) is installed and configured.
2. Open **HACS → Integrations**.
3. Open the three-dot menu and choose **Custom repositories**.
4. Add this repository URL:

   ```text
   https://github.com/gianmarco112/ha-teams-presence
   ```

5. Select **Integration** as the category and click **Add**.
6. Find **Microsoft Teams Presence** in HACS and install it.
7. Restart Home Assistant.
8. Go to **Settings → Devices & services → Add integration** and search for **Microsoft Teams Presence**.

You can also use the [My Home Assistant HACS repository link](https://my.home-assistant.io/redirect/hacs_repository/?owner=gianmarco112&repository=ha-teams-presence&category=integration).

### Manual installation

1. Download the [repository ZIP](https://github.com/gianmarco112/ha-teams-presence/archive/refs/heads/main.zip).
2. Copy `custom_components/teams_presence` into `/config/custom_components/teams_presence`.
3. Restart Home Assistant.
4. Add the integration from **Settings → Devices & services**.

## Microsoft Entra ID setup

1. Open the [Microsoft Entra admin center](https://entra.microsoft.com/).
2. Create a dedicated **App registration** for Home Assistant.
3. Choose the account type appropriate for your organization (normally single-tenant).
4. Copy the **Directory (tenant) ID** and **Application (client) ID**.
5. Open **Certificates & secrets** and create a client secret. Copy the secret **Value** immediately; it is shown only once.
6. Open **API permissions → Add a permission → Microsoft Graph → Application permissions**.
7. Add `User.Read.All` and `Presence.Read.All`.
8. Select **Grant admin consent** and verify that both permissions show as granted.
9. In Home Assistant, add the integration and enter your own tenant ID, client ID and client-secret value.

**Never publish your tenant ID, client ID, client secret, access token, user list or organization-specific logs.** The repository contains no tenant configuration or credentials. Each Home Assistant administrator supplies their own values locally during setup.

## Configuration and account filtering

The integration is configured entirely through the Home Assistant UI. After setup, open the integration's **Configure** page to manage excluded users.

The integration monitors the users returned by the Microsoft Graph `/users` endpoint. It does not automatically filter guest, disabled or other account types. To omit an account, select it manually in **Excluded users** in the integration options.

**Shared mailboxes:** Microsoft Graph does not provide a universally reliable mailbox-type indicator in the fields currently used by this integration. Exclude shared mailboxes manually in the integration options.

## Sensors

The integration creates one sensor per monitored user. The sensor state reflects the Graph `availability` value, normalized to Home Assistant-friendly values where possible.

| Microsoft Graph availability | Sensor state |
|---|---|
| `Available` | `available` |
| `Busy` | `busy` |
| `DoNotDisturb` | `dnd` |
| `Away` | `away` |
| `BeRightBack` | `brb` |
| `Offline` | `offline` |
| `PresenceUnknown` / missing | `unknown` |

Additional attributes include the display name, email/UPN, Graph availability, activity and user ID. Treat these attributes as personal/organizational data and restrict access to dashboards and automations accordingly.

## Troubleshooting

| Symptom | What to check |
|---|---|
| Setup reports it cannot connect | Verify tenant ID, client ID and the client-secret **value**; check that the secret has not expired |
| HTTP 401 | Recreate or renew the client secret and verify the tenant and application IDs |
| HTTP 403 | Confirm both Graph **Application** permissions and tenant-wide admin consent |
| No users are discovered | Check that the app can read users with `User.Read.All`, then check the `teams_presence` diagnostics in Home Assistant logs |
| Shared mailbox appears | Add it to **Excluded users** manually |
| Presence is `unknown` | The user sensor is still created if the presence endpoint fails; check `Presence.Read.All`, admin consent and the `teams_presence` warning/error in Home Assistant logs |
| Exclusion changes do not appear immediately | The integration reloads after its options are saved; allow the reload to finish |

For diagnostics, open **Settings → System → Logs** and look for `teams_presence`. Before sharing logs in a public issue, redact tenant IDs, user IDs, UPNs, email addresses, tokens and other identifying information.

## Privacy and security

- Credentials are entered into the local Home Assistant config entry; they are not sent to this GitHub repository.
- The integration communicates with Microsoft identity and Microsoft Graph endpoints to authenticate, discover users and read presence.
- Presence and account attributes can reveal employee activity. Deploy only with the authorization, transparency and retention practices required by your organization and applicable law.
- Use a dedicated Entra app registration and protect Home Assistant backups, configuration storage and administrator access.
- Never include secrets, access tokens, tenant-specific exports, real user lists or unredacted logs in issues, pull requests or screenshots.

## Compatibility and validation

This repository follows the HACS integration repository layout, includes `hacs.json`, local Home Assistant brand assets, a HACS validation workflow and a Home Assistant **hassfest** workflow. GitHub Actions run on pushes, pull requests and manual dispatches.

A green validation workflow checks repository/HACS metadata and Home Assistant integration metadata; it does **not** replace testing the integration against your actual Microsoft 365 tenant and Home Assistant installation. The project is currently an early community release and is not affiliated with Microsoft or the Home Assistant project.

## Development

The repository is intentionally limited to one integration under `custom_components/teams_presence/`, as required for a HACS integration repository.

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and use the issue templates. Do not submit real credentials, personal data or organization-specific exports.

## License

Distributed under the [MIT License](LICENSE).

---

<div align="center">

Made for Home Assistant · Powered by Microsoft Graph

</div>
