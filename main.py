from dotenv import load_dotenv
load_dotenv()

import time
import traceback
import asyncio

from twitter_api import *
from helper import *

text_synth = twitter.get_user("TextSynth").id_str
    
class Listener(tweepy.StreamListener):
    def on_status(self, status):

        if status.user.screen_name == "TextSynth":
            return

        asyncio.get_event_loop().run_until_complete(reply(twitter, status))

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
        stream.filter(track=["@TextSynth"], follow=[text_synth], is_async=True)
    except Exception as e:
        traceback.print_exc()
        for status in tweepy.Cursor(twitter.home_timeline).items(4):
                asyncio.get_event_loop().run_until_complete(reply(twitter, status))
        time.sleep(60 * 60)
