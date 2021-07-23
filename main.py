from dotenv import load_dotenv
import _thread
load_dotenv()

import time
import traceback

from twitter_api import *
from helper import *

import random

    
class Listener(tweepy.StreamListener):
    def on_status(self, status):
        if status.user.screen_name == "TextSynth":
            return


        reply(twitter, status)


    def on_error(self, status_code):
        if status_code == 420:
            print("ahhhh")
            return False
        
        print(status_code)

stream = tweepy.Stream(auth, Listener())


while True:
    try:
        try:
            stream.filter(track=["@TextSynth"])
        except:
            pass

        try:
            for status in tweepy.Cursor(twitter.home_timeline).items(20):
                reply(twitter, status)
        except:
            time.sleep(10)
            continue

        time.sleep(random.randrange(60, 120) * 60)

    except Exception as e:
        traceback.print_exc()
        time.sleep(10)
