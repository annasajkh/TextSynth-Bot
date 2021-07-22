from dotenv import load_dotenv
load_dotenv()

import time
import traceback

from twitter_api import *
from helper import *

import random

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
        stream.filter(track=["@TextSynth"], is_async=True)

        for tweet in tweepy.Cursor(twitter.home_timeline).items(100):
            if not tweet.favorited:
                memory[tweet.user.name] = []
                reply(twitter, tweet, memory)
                time.sleep(random.randrange(0,3))
                tweet.favorite()

        time.sleep(random.randrange(60, 120))

    except Exception as e:
        traceback.print_exc()
        time.sleep(10)