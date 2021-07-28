from dotenv import load_dotenv
load_dotenv()

import time
import traceback

from twitter_api import *
from helper import *
import _thread

def reply_thread(thread_name):
    print(thread_name + " starting")

    class Listener(tweepy.StreamListener):
        def on_status(self, status):

            if status.user.screen_name == "TextSynth":
                return

            print("trying to reply to " + status.user.screen_name)

            reply(twitter, status)

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

    while True:
        text = get_gpt(finetune + "\nBot: ")
        text = re.split(".*?:",text)[0].strip()[:280]
        try:
            twitter.update_status(text)
        except:
            continue

        for status in tweepy.Cursor(twitter.home_timeline).items(5):
            reply(twitter, status)

        time.sleep(60 * 60)

_thread.start_new_thread(reply_thread, ("reply thread",))
_thread.start_new_thread(tweet_thread, ("tweet thread",))

while 1:
    pass