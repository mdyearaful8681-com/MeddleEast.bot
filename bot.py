import os
import re
from telethon import TelegramClient, events
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

# টেলিগ্রাম API কনফিগারেশন
api_id = 32140940
api_hash = '02d8866c09ba53e70b7cdb9dbcca9342'

# এখানে আপনার টেলিগ্রাম সেশন স্ট্রিং (Session String) বসাতে হবে 
# (যদি লোকাল সেশন ফাইল ব্যবহার না করে String Session দিতে চান, তবে নিচে স্ট్రిং বসিয়ে দিন)
SESSION_STRING = os.environ.get('SESSION_STRING', '') 

source_channels = ['Intelslava', 'DDGeopolitics', 'geopolitics_prime']
my_channel = '@MiddleEastEnglis'
channel_credit = "\n\nFollow me: @MiddleEastEnglis"

# টেলিগ্রাম ক্লায়েন্ট ইনিশিয়ালাইজেশন (স্ট্রিং সেশন বা মেমোরি বেসড সেশন ব্যবহার করার জন্য)
if SESSION_STRING:
    from telethon.sessions import StringSession
    client = TelegramClient(StringSession(SESSION_STRING), api_id, api_hash, system_version='4.16.3-vx')
else:
    # যদি এনভায়রনমেন্ট ভ্যারিয়েবলে স্ট্রিং না থাকে, তবে মেমোরি সেশন ব্যবহার করবে যাতে রেন্ডারে ফাইল ক্র্যাশ না করে
    client = TelegramClient('anon', api_id, api_hash, system_version='4.16.3-vx')

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    if event.raw_text:
        text = event.raw_text
        
        # ১. সমস্ত লিংক, ওয়েবসাইট এবং সোর্স চ্যানেলের ইউজারনেম বা ক্রেডিট কঠোরভাবে মুছে ফেলা
        clean_text = re.sub(r'http\S+|www\S+|@\w+|t\.me\/\S+|Source:.*|Via:.*|Credit:.*', '', text, flags=re.IGNORECASE).strip()[:900]
        
        # ২. অন্য কোনো সোর্সের নাম বা ক্রেডিট না রেখে শুধুমাত্র নিজের চ্যানেল ক্রেডিট যুক্ত করা
        final_caption = clean_text + channel_credit
        
        try:
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
