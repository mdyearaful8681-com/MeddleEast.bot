import os
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
from threading import Thread

# Koyeb বা Render সার্ভারের জন্য ছোট ওয়েব সার্ভার (পোর্ট ৮০৮০)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# আপনার সঠিক টেলিগ্রাম API কনফিগারেশন
api_id = 37007922
api_hash = '06daa70876742419f268ffaadc42a251'

# রেন্ডারে সেভ করা String Session
string_session = os.environ.get('SESSION_STRING', '')

# আপনার দেওয়া নতুন সোর্স চ্যানেলগুলোর তালিকা (সঠিক ইউজারনেম ফরম্যাটে)
source_channels = [
    '@QudsNen',
    '@Irna_en',
    '@rtnews',
    '@MFARussia',
    '@CIG_telegram',
    '@ClashReport',
    '@infodefENGLAND',
    '@Middle_East_Spectator',
    '@Slavyangrad',
    '@geopolitics_prime',
    '@DDGeopolitics',
    '@Intelslava'
]

my_channel = '@MiddleEastEnglis'
channel_credit = "\n\nFollow me: @MiddleEastEnglis"

# ডুপ্লিকেট নিউজ আটকানোর জন্য প্রসেসড মেসেজ আইডি ট্র্যাক করার সেট
processed_ids = set()

# StringSession ব্যবহার করে ক্লায়েন্ট ইনিশিয়ালাইজেশন
client = TelegramClient(StringSession(string_session), api_id, api_hash, system_version='4.16.3-vx')

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    try:
        # একই নিউজ বারবার আসা রোধ করতে মেসেজ আইডি ও চ্যাট আইডি চেক করা
        message_unique_key = (event.chat_id, event.id)
        if message_unique_key in processed_ids:
            return
        
        # মেমরি লিমিটেডের মধ্যে রাখতে সেট সাইজ নিয়ন্ত্রণ করা (সর্বোচ্চ ২০০০টি আইডি সেভ থাকবে)
        if len(processed_ids) > 2000:
            processed_ids.clear()
            
        processed_ids.add(message_unique_key)

        if event.raw_text:
            text = event.raw_text
            
            # ১. সমস্ত লিংক (http, www, t.me), চ্যানেলের ইউজারনেম (@username), এবং যেকোনো সোর্স/ক্রেডিট বা মাধ্যম কঠোরভাবে মুছে ফেলা
            clean_text = re.sub(
                r'http\S+|www\S+|@\w+|t\.me\/\S+|Source:.*|Via:.*|Credit:.*|频道:.*|Telegram:.*', 
                '', 
                text, 
                flags=re.IGNORECASE
            ).strip()[:900]
            
            # যদি টেক্সট একেবারে ফাঁকা হয়ে যায় তবে ফরোয়ার্ড করার দরকার নেই
            if not clean_text and not event.media:
                return

            # ২. সোর্সের কোনো নাম বা ক্রেডিট না রেখে শুধুমাত্র নিজের চ্যানেল ক্রেডিট যুক্ত করা
            final_caption = clean_text + channel_credit if clean_text else channel_credit.strip()
            
            # ৩. মিডিয়া থাকলে ক্যাপশনসহ এবং না থাকলে শুধুমাত্র টেক্সট পাঠানো
            if event.media and not getattr(event.media, 'webpage', None):
                await client.send_file(my_channel, event.media, caption=final_caption)
            else:
                await client.send_message(my_channel, final_caption)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    keep_alive()
    print("বট ক্লাউডে চালু হচ্ছে...")
    client.start()
    client.run_until_disconnected()
