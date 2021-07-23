from dotenv import load_dotenv
load_dotenv()

import time
import traceback

from twitter_api import *
from helper import *

    
class Listener(tweepy.StreamListener):
    def on_status(self, status):
        time.sleep(random.uniform(0,2))
        
        try:
            twitter.create_favorite(status.id)
        except:
            return

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
        print("bot starting...")
        stream.filter(track=["@TextSynth"])
    except Exception as e:
        traceback.print_exc()
        time.sleep(10)
