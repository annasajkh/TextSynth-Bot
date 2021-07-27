from dotenv import load_dotenv
load_dotenv()

import time
import traceback
import asyncio

from twitter_api import *
from helper import *

class Listener(tweepy.StreamListener):
    def on_status(self, status):

        if status.user.screen_name == "TextSynth":
            return

        print("trying to reply to " + status.user.screen_name)

        asyncio.get_event_loop().run_until_complete(reply(twitter, status))

        if random.random() > 0.99:
            text = asyncio.get_event_loop().run_until_complete(get_gpt(finetune + "\nBot: "))
            text = re.split(".*?:",text)[0].strip()[:280]

            twitter.update_status(text)

    def on_error(self, status_code):
        if status_code == 420:
            print("ahhhh")
            time.sleep(20)
            return False
        
        print(status_code)

stream = tweepy.Stream(auth, Listener())

while True:
    try:
        print("bot starting...")
        stream.filter(track=["@TextSynth"])
    except Exception as e:
        traceback.print_exc()
        time.sleep(10)
