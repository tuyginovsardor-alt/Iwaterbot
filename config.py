import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPER_ADMIN_ID = os.getenv("SUPER_ADMIN_ID")

# Domain for the website
DOMAIN = os.getenv("DOMAIN")
