import asyncio
from dotenv import load_dotenv
load_dotenv()

import time
import traceback

from twitter_api import *
from helper import *
import _thread

from flask import Flask

app = Flask(__name__)



def reply_thread(thread_name):
    print(thread_name + " starting")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    session = loop.run_until_complete(get_session())


    class Listener(tweepy.StreamListener):
        def on_status(self, status):

            if hasattr(status, "retweeted_status"):
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
            stream.filter(track=["@TextSynth"])
        except Exception as e:
            traceback.print_exc()
            time.sleep(10)


def tweet_thread(thread_name):
    print(thread_name + " starting")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    session = loop.run_until_complete(get_session())
    

    while True:
        result = loop.run_until_complete(get_gpt(finetune_tweet, 1, 50, 1, session))
        result = result.split("\n")[0].strip()

        while result.strip() == "" or "!!" in result or "??" in result or "~~" in result or "_" in result or "**" in result:
            result = loop.run_until_complete(get_gpt(finetune_tweet, 1, 50, 1,  session))
            result = result.split("\n")[0].strip()

            time.sleep(10)

        try:
            twitter.update_status(result)
        except:
            traceback.print_exc()
            continue

        time.sleep(60 * 60)


@app.route('/')
def main():
  return "your bot is alive"


def run():
  from waitress import serve
  serve(app, host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()

keep_alive()

_thread.start_new_thread(reply_thread, ("reply thread",))
_thread.start_new_thread(tweet_thread, ("tweet thread",))

while 1:
    pass