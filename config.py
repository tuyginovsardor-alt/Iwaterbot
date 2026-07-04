import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPER_ADMIN_ID = os.getenv("SUPER_ADMIN_ID")

# Super admin and potential extra admins
ADMIN_IDS = []
if SUPER_ADMIN_ID and SUPER_ADMIN_ID.isdigit():
    ADMIN_IDS.append(int(SUPER_ADMIN_ID))

env_admin_ids = os.getenv("ADMIN_IDS", "")
for admin_id in env_admin_ids.split(","):
    admin_id = admin_id.strip()
    if admin_id.isdigit():
        val = int(admin_id)
        if val not in ADMIN_IDS:
            ADMIN_IDS.append(val)

# Domain for the website
DOMAIN = os.getenv("DOMAIN")
