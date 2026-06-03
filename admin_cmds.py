import asyncio
from telethon import events, TelegramClient
from telethon.sessions import StringSession
import core.clients as clients_module
from core.clients import main_app, auth_filter, army_clients
from core.config import API_ID, API_HASH, config_data, save_config

@main_app.on(events.NewMessage(pattern=r'^\.addsession (.+)', func=auth_filter))
async def add_session_handler(event):
    session_string = event.pattern_match.group(1).strip()
    
    try:
        new_client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
        await new_client.start()
        army_clients.append(new_client)
        
        if session_string not in config_data["SESSIONS"]:
            config_data["SESSIONS"].append(session_string)
            save_config()
            
        resp = await event.reply(f"✅ Session {len(army_clients)} added successfully!")
    except Exception as e:
        resp = await event.reply(f"❌ Failed to add session: {e}")
        
    await event.delete()
    await asyncio.sleep(3)
    await resp.delete()

@main_app.on(events.NewMessage(pattern=r'^\.me (on|off)$', func=auth_filter))
async def me_handler(event):
    state = event.pattern_match.group(1).lower()
    if state == "on":
        config_data["OWNER_PARTICIPATE"] = True
        msg = "✅ Owner will now participate in raids."
    else:
        config_data["OWNER_PARTICIPATE"] = False
        msg = "❌ Owner will NOT participate in raids."
    save_config()
    resp = await event.reply(msg)
    await event.delete()
    await asyncio.sleep(2)
    await resp.delete()

@main_app.on(events.NewMessage(pattern=r'^\.sudo(?: |$)(.*)', func=auth_filter))
async def add_sudo(event):
    if event.sender_id != clients_module.OWNER_ID:
        return
        
    target = None
    arg = event.pattern_match.group(1).strip()
    
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if reply_msg and reply_msg.sender_id:
            target = await reply_msg.get_sender()
    elif arg:
        try:
            target = await main_app.get_entity(int(arg) if arg.isdigit() else arg)
        except:
            pass
            
    if not target:
        resp = await event.reply("Specify user to add to Sudo.")
        await asyncio.sleep(2)
        await resp.delete()
        return
        
    if target.id not in config_data["SUDO_USERS"]:
        config_data["SUDO_USERS"].append(target.id)
        save_config()
        
    sender = await event.get_sender()
    owner_name = getattr(sender, 'first_name', 'Owner') or 'Owner'
    target_name = getattr(target, 'first_name', 'User') or 'User'
    
    text = f"""```╭━━━━⟬🛡️ SUDO USER ADDED⟭━━━━╮
┃                           
┃ ✦➣ 🎯 Target: {target_name}
┃                           
┃ ✦➣ 🛡️ Status: Promoted to Sudo
┃                           
┃ ✦➣ 🏷️ Authorized by {owner_name}
┃                           
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯```"""
    resp = await event.reply(text)
    await event.delete()

@main_app.on(events.NewMessage(pattern=r'^\.rmsudo(?: |$)(.*)', func=auth_filter))
async def rm_sudo(event):
    if event.sender_id != clients_module.OWNER_ID:
        return
        
    target = None
    arg = event.pattern_match.group(1).strip()
    
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if reply_msg and reply_msg.sender_id:
            target = await reply_msg.get_sender()
    elif arg:
        try:
            target = await main_app.get_entity(int(arg) if arg.isdigit() else arg)
        except:
            pass
            
    if not target:
        resp = await event.reply("Specify user to remove from Sudo.")
        await asyncio.sleep(2)
        if resp: await resp.delete()
        return
        
    if target.id in config_data["SUDO_USERS"]:
        config_data["SUDO_USERS"].remove(target.id)
        save_config()
        
    sender = await event.get_sender()
    owner_name = getattr(sender, 'first_name', 'Owner') or 'Owner'
    target_name = getattr(target, 'first_name', 'User') or 'User'
    
    text = f"""```╭━━━━⟬🛡️ SUDO USER REMOVED⟭━━━━╮
┃                           
┃ ✦➣ 🎯 Target: {target_name}
┃                           
┃ ✦➣ 🛡️ Status: Demoted from Sudo
┃                           
┃ ✦➣ 🏷️ Authorized by {owner_name}
┃                           
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯```"""
    resp = await event.reply(text)
    await event.delete()
