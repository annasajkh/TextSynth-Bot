from dotenv import load_dotenv
load_dotenv()

import time
import traceback

from twitter_api import *
from helper import *

memory = {}


class Listener(tweepy.StreamListener):
    def on_status(self, status):
        if status.user.screen_name == "TextSynth":
            return
        
        reply(twitter, status, memory)

    def on_error(self, status_code):
        if status_code == 420:
            print("ahhhh")
            return False
        
        print(status_code)


stream = tweepy.Stream(auth, Listener())



while True:
    try:
        stream.filter(track=["@TextSynth"])
    except Exception as e:
        traceback.print_exc()
        time.sleep(10)