# Security Policy

## Supported versions

Security fixes are targeted at the latest version on the default branch and the latest published release.

## Reporting a vulnerability

Please use GitHub's **Report a vulnerability** feature in the Security tab to send a private report. Do not open a public issue for suspected vulnerabilities.

Never include actual tenant IDs, client IDs, client secrets, access tokens, employee identifiers, email addresses, user exports or unredacted logs in public reports.

## Deployment guidance

Use a dedicated Microsoft Entra app registration, review the tenant-wide Microsoft Graph Application permissions with an administrator, secure Home Assistant backups and restrict access to presence dashboards.
