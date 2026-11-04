DOMAIN = "teams_presence"

CONF_TENANT_ID = "tenant_id"
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_EXCLUDED_USERS = "excluded_users"

DEFAULT_SCAN_INTERVAL = 60
GRAPH_BASE = "https://graph.microsoft.com/v1.0"
TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"

ATTR_ACTIVITY = "activity"
ATTR_AVAILABILITY = "availability"
ATTR_DISPLAY_NAME = "display_name"
ATTR_EMAIL = "email"
ATTR_USER_ID = "user_id"

STATUS_MAP = {
    "Available": "available",
    "Busy": "busy",
    "DoNotDisturb": "dnd",
    "Away": "away",
    "BeRightBack": "brb",
    "Offline": "offline",
    "PresenceUnknown": "unknown",
}
