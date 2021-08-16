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

    session = loop.run_until_complete(get_session())

    deepleffen = twitter.get_user("DeepLeffen").id_str
    gpt2upaguy = twitter.get_user("gpt2upaguy").id_str
    dril_gpt2  = twitter.get_user("dril_gpt2").id_str
    drilbot_neo = twitter.get_user("drilbot_neo").id_str


    class Listener(tweepy.StreamListener):
        def on_status(self, status):

            if status.retweeted:
                return

            mentions = [user["screen_name"] for user in status.entities["user_mentions"]]
            print(mentions)

            for user in ["DeepLeffen", "gpt2upaguy", "dril_gpt2", "drilbot_neo"]:
                if user in mentions and "TextSynth" not in mentions:
                    return

            if status.user.screen_name == "TextSynth":
                return

            print("trying to reply to " + status.user.screen_name)

            try:
                reply(twitter, status, session, loop)
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
            stream.filter(track=["@TextSynth"], follow=[deepleffen, gpt2upaguy, dril_gpt2, drilbot_neo])
        except Exception as e:
            traceback.print_exc()
            time.sleep(10)

def tweet_thread(thread_name):
    print(thread_name + " starting")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    session = loop.run_until_complete(get_session())
    

    while True:

        result = loop.run_until_complete(get_gpt(finetune_tweet, session))
        result = result.split("tweet:")[0].strip()

        try:
            twitter.update_status(result)
        except:
            traceback.print_exc()
            continue

        time.sleep(60 * 60)


_thread.start_new_thread(reply_thread, ("reply thread",))
_thread.start_new_thread(tweet_thread, ("tweet thread",))

while 1:
    pass