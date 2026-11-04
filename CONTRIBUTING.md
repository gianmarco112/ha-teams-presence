# Contributing

Thanks for helping improve Microsoft Teams Presence.

## Before opening an issue or pull request

- Search existing issues to avoid duplicates.
- Describe your Home Assistant Core version and integration version.
- Include the relevant error and steps to reproduce.
- Redact tenant IDs, client IDs, user IDs, email addresses, UPNs, tokens, URLs containing tenant data and all secrets.
- Never attach a real user export, a Home Assistant backup or a screenshot containing credentials or personal data.

## Pull requests

- Keep the repository to one integration under `custom_components/teams_presence/`.
- Follow Home Assistant conventions and keep translations in sync (`strings.json`, `translations/en.json`, `translations/it.json`).
- Run JSON parsing and Python syntax checks before submitting.
- Ensure the HACS and hassfest GitHub Actions pass.
- Explain user-visible changes and update the README where needed.

## Security reports

Do not report vulnerabilities publicly. Use the private vulnerability reporting feature on the GitHub Security tab, when available.
