import re
import asyncio
from telethon import events
from core.clients import main_app, auth_filter
from core.raid_manager import start_ra_raid, start_custom_raid, start_reply_raid, active_ra_raids, active_custom_raids, active_reply_raids

@main_app.on(events.NewMessage(pattern=r'^\.rr(\d+)(?: |$)(.*)', func=auth_filter))
async def rr_handler(event):
    count = int(event.pattern_match.group(1))
    target_user = None
    arg = event.pattern_match.group(2).strip()
    
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if reply_msg and reply_msg.sender_id:
            target_user = reply_msg.sender_id
    elif arg:
        try:
            ent = await main_app.get_entity(int(arg) if arg.isdigit() else arg)
            target_user = ent.id
        except Exception:
            pass
        
    if not target_user:
        resp = await event.reply("Reply to a user or provide an ID to activate reply raid.")
        await event.delete()
        await asyncio.sleep(2)
        await resp.delete()
        return
    
    # Only register the target — don't fire yet. Wait for their incoming message.
    chat_id = event.chat_id
    if chat_id not in active_reply_raids:
        active_reply_raids[chat_id] = {}
    active_reply_raids[chat_id][target_user] = count
        
    resp = await event.reply(f"🔥 Reply Raid Armed! Waiting for target's message ({count} per session).")
    await event.delete()
    await asyncio.sleep(2)
    await resp.delete()

@main_app.on(events.NewMessage())
async def rr_watcher(event):
    if not event.sender_id:
        return
        
    chat_id = event.chat_id
    user_id = event.sender_id
    
    if chat_id in active_reply_raids and user_id in active_reply_raids.get(chat_id, {}):
        count = active_reply_raids[chat_id][user_id]
        sender = await event.get_sender()
        first_name = getattr(sender, 'first_name', 'User') or 'User'
        # Fire the raid replying to THIS specific incoming message
        start_reply_raid(chat_id, user_id, count, event.id, first_name)

@main_app.on(events.NewMessage(pattern=r'^\.ra(?: |$)(.*)', func=auth_filter))
async def ra_handler(event):
    target_user = None
    arg = event.pattern_match.group(1).strip()
    reply_to_msg_id = None
    
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if reply_msg and reply_msg.sender_id:
            target_user = await reply_msg.get_sender()
            reply_to_msg_id = reply_msg.id
    elif arg:
        try:
            target_user = await main_app.get_entity(int(arg) if arg.isdigit() else arg)
        except Exception:
            pass

    if not target_user:
        return

    first_name = getattr(target_user, 'first_name', 'User') or 'User'
    resp = await event.reply(f"🔥 Continuous Raid Activated on {first_name}")
    await event.delete()
    
    mention = f'<a href="tg://user?id={target_user.id}">{first_name}</a>'
    start_ra_raid(event.chat_id, mention, reply_to=reply_to_msg_id)
    
    await asyncio.sleep(2)
    await resp.delete()

@main_app.on(events.NewMessage(pattern=r'^\.raid\s', func=auth_filter))
async def raid_custom_handler(event):
    # Get the full raw text preserving all newlines
    raw_text = event.text
    
    # Remove the ".raid " prefix
    content = raw_text[6:]  # len(".raid ") = 6
    
    if not content.strip():
        return
    
    # Extract user IDs/usernames from the beginning of the first line
    # User IDs and @usernames appear at the start, separated by spaces
    # The message starts at the first word that isn't an ID or @username
    first_line = content.split("\n")[0]
    first_line_parts = first_line.split(" ")
    
    user_ids = []
    msg_start_idx = 0  # character index in content where the message starts
    
    consumed_len = 0
    for p in first_line_parts:
        if p.isdigit() or p.startswith("@"):
            user_ids.append(p)
            consumed_len += len(p) + 1  # +1 for the space
        else:
            break
    
    if not user_ids:
        return
        
    # The custom message is everything after the user IDs
    custom_msg = content[consumed_len:] 
    
    if not custom_msg.strip():
        return
    
    mentions = []
    for uid in user_ids:
        if uid.startswith("@"):
            mentions.append(uid)
        else:
            try:
                ent = await main_app.get_entity(int(uid) if uid.isdigit() else uid)
                first = getattr(ent, 'first_name', str(uid)) or str(uid)
                mentions.append(f'<a href="tg://user?id={uid}">{first}</a>')
            except Exception:
                mentions.append(f'<a href="tg://user?id={uid}">{uid}</a>')
            
    final_text = " ".join(mentions) + " " + custom_msg
    
    resp = await event.reply("🔥 Custom Raid Activated.")
    await event.delete()
    
    start_custom_raid(event.chat_id, final_text)
    
    await asyncio.sleep(2)
    await resp.delete()

@main_app.on(events.NewMessage(pattern=r'^\.stop$', func=auth_filter))
async def stop_handler(event):
    chat_id = event.chat_id
    if chat_id in active_ra_raids:
        active_ra_raids[chat_id] = False
    if chat_id in active_custom_raids:
        active_custom_raids[chat_id] = False
    if chat_id in active_reply_raids:
        active_reply_raids[chat_id] = {}
        
    resp = await event.reply("🛑 All raids stopped in this chat.")
    await event.delete()
    await asyncio.sleep(2)
    await resp.delete()

@main_app.on(events.NewMessage(pattern=r'^\.srr$', func=auth_filter))
async def srr_handler(event):
    chat_id = event.chat_id
    if chat_id in active_reply_raids:
        active_reply_raids[chat_id] = {}
    resp = await event.reply("🛑 Reply raid (.rr) stopped.")
    await event.delete()
    await asyncio.sleep(2)
    await resp.delete()

@main_app.on(events.NewMessage(pattern=r'^\.sra$', func=auth_filter))
async def sra_handler(event):
    chat_id = event.chat_id
    if chat_id in active_ra_raids:
        active_ra_raids[chat_id] = False
    resp = await event.reply("🛑 Continuous raid (.ra) stopped.")
    await event.delete()
    await asyncio.sleep(2)
    await resp.delete()

@main_app.on(events.NewMessage(pattern=r'^\.straid$', func=auth_filter))
async def straid_handler(event):
    chat_id = event.chat_id
    if chat_id in active_custom_raids:
        active_custom_raids[chat_id] = False
    resp = await event.reply("🛑 Custom raid (.raid) stopped.")
    await event.delete()
    await asyncio.sleep(2)
    await resp.delete()
