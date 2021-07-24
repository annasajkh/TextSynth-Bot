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

        asyncio.get_event_loop().run_until_complete(attempt_to_reply(twitter, status))

        try:
            for s in tweepy.Cursor(twitter.home_timeline).items(20):
                asyncio.get_event_loop().run_until_complete(attempt_to_reply(twitter, s))
                time.sleep(10)
        except:
            traceback.print_exc()


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
