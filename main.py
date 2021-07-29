import asyncio
from dotenv import load_dotenv
load_dotenv()

import time
import traceback

from twitter_api import *
from helper import *
import _thread


def reply_thread(thread_name):
    print(thread_name + " starting")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    


    class Listener(tweepy.StreamListener):
        def on_status(self, status):

            if status.user.screen_name == "TextSynth":
                return

            print("trying to reply to " + status.user.screen_name)

            try:
                loop.run_until_complete(reply(twitter, status))
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

def tweet_thread(thread_name):
    
    print(thread_name + " starting")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    

    while True:
        text = loop.run_until_complete(get_gpt(finetune + "\nJack:"))
        text = re.split(".*?:",text)[0].strip()[:280]

        try:
            twitter.update_status(text)
        except:
            traceback.print_exc()
            continue

        time.sleep(60 * 60)


_thread.start_new_thread(reply_thread, ("reply thread",))
_thread.start_new_thread(tweet_thread, ("tweet thread",))

while 1:
    pass