import os
import asyncio
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import EditBannedRequest, GetFullChannelRequest
from telethon.tl.functions.phone import GetGroupParticipantsRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins

API_ID = 32815595
API_HASH = "4f8710ec9e88946139ac688af9eb1f5b"

# पहली सेशन स्ट्रिंग (आप इसे चाहें तो यहाँ डायरेक्ट लिख सकते हैं या एनवायरनमेंट वेरिएबल से ले सकते हैं)
SESSION_STRING_1 = "1BVtsOIwBu6MnF8lzk1aUMffZYqOLKa3zh1zfVjvmbxam_WsyW6YmfQwFq6VVMLAkOYXMqMPLfy0GNvz07eWnJZKTqa0uP-tKANTlDYlkWTkVe8d0jtSR4BOuhFBxysWLE92KFZJNX6aMA3QSLVabC1-qQLEHOpeKwfIPihG1UTGlvbA--1_8s18pCJUYzrr2Z9e2lMd1yn4IhbzUYWUwp7CcdmkMWsMu9M-zQoDYp25auPqFFky-AEf6a92D5vxQgPu4vUdkqOIKruQd2r1jZpshANuDzm8UzussHCqlSy6OPEkgsk-ytPyfX65B6jzCcbsvCoNh2UwUDlobJgUSf-IUWhjS-Ho="

# दूसरी सेशन स्ट्रिंग (जो आपने अभी हाल ही में जनरेट की है)
SESSION_STRING_2 = "1BVtsOIcBuyReuoPFKXHXpq5DjmUUUyn3KwNVt_Yl3VEU9BPSOQe96ICR5Tn27BO5mxSLpyozeKNcuLRuk2z89DwvbsP1agTRPggz6BhSwe6Pm_JZAKrnpcb-D-RRMLmtHdM4gaoall_SlBAr8BXfj53sSjM5shOMwiPDAluc2SFKM5YmDNgQ9b8s_xu5kMkh06LI84Boy6UCcZ6fCTlxFL5KRJwPgQ-XP3nqMtAF13Zof6ainF0R1uFsIlBrzpt-PRf5Ut6_Yhn5Q_zUPKMZr3mwQh2kEMKukTUlb8M1JcvTK6nCQXnfHBRFNeK7N1UfxbHGom0Nb6VnAnapK9-qrH2dPsfohgo="

app = Flask(__name__)

@app.route("/")
def home():
    return "Both Telegram Voice Chat Userbots are running actively!"

# दो अलग-अलग क्लाइंट बनाना
client1 = TelegramClient(StringSession(SESSION_STRING_1), API_ID, API_HASH)
client2 = TelegramClient(StringSession(SESSION_STRING_2), API_ID, API_HASH)

BAN_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
    send_polls=True,
    change_info=False,
    invite_users=False,
    pin_messages=False
)

async def run_bot_instance(client_instance, bot_name):
    await client_instance.start()
    print(f"{bot_name} शुरू हो गया है!")
    
    while True:
        try:
            async for dialog in client_instance.iter_dialogs():
                chat = dialog.entity
                
                is_channel = getattr(chat, "broadcast", False)
                is_megagroup = getattr(chat, "megagroup", False)
                
                if not (is_channel or is_megagroup):
                    continue
                
                try:
                    full_chat = await client_instance(GetFullChannelRequest(chat))
                    call = full_chat.full_chat.call
                    
                    if not call:
                        continue 
                    
                    admins = {admin.id async for admin in client_instance.iter_participants(chat, filter=ChannelParticipantsAdmins)}
                    
                    call_participants = await client_instance(GetGroupParticipantsRequest(
                        call=call,
                        ids=[],
                        sources=[],
                        offset='',
                        limit=100
                    ))
                    
                    for participant in call_participants.participants:
                        try:
                            user_id = participant.peer.user_id
                        except AttributeError:
                            continue
                        
                        if user_id in admins:
                            continue
                        
                        try:
                            user = await client_instance.get_entity(user_id)
                            if user.bot or user.id == (await client_instance.get_me()).id:
                                continue
                                
                            is_premium = getattr(user, "premium", False) or getattr(user, "emoji_status", None) is not None
                            
                            if is_premium:
                                await client_instance(EditBannedRequest(chat, user_id, BAN_RIGHTS))
                        except Exception:
                            pass
                                
                except Exception:
                    continue
                    
        except Exception:
            pass
            
        await asyncio.sleep(0.05)

def start_bot_1():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot_instance(client1, "Bot 1"))

def start_bot_2():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot_instance(client2, "Bot 2"))

if __name__ == "__main__":
    import threading
    # दोनों बोट्स को अलग-अलग थ्रेड्स में एक साथ चलाना
    threading.Thread(target=start_bot_1, daemon=True).start()
    threading.Thread(target=start_bot_2, daemon=True).start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
  
