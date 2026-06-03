from telethon import TelegramClient
from core.config import API_ID, API_HASH, config_data

main_app = TelegramClient("main_session", API_ID, API_HASH)
army_clients = []
OWNER_ID = None

def get_active_clients():
    clients = list(army_clients)
    if config_data.get("OWNER_PARTICIPATE", False):
        clients.append(main_app)
    return clients

def auth_filter(event):
    if not event.sender_id:
        return False
    return event.sender_id == OWNER_ID or event.sender_id in config_data["SUDO_USERS"]
