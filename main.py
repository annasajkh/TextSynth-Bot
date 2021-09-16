import asyncio
from dotenv import load_dotenv

load_dotenv()

import time
import traceback

from twitter_api import *
from helper import *
import _thread
from threading import Thread

import requests
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

def get_tweet():
    finetune = """
    if anyone feels like getting a snack after this shit post please do#
    i've lost faith in my own opinions#
    wtf? i just farted#
    the rain is pretty but i don't wanna go outside and be wet#
    yumyum i want to make baby with you#
    i was doing dishes when i accidentally dropped the bowl, hard!#
    """.strip()

    params = {
        "prompt": finetune,
        "numResults": 1,
        "maxTokens": 100,
        "stopSequences": ["#"],
        "topKReturn": 0,
        "temperature": 1.0
    }

    response = requests.post(
        "https://api.ai21.com/studio/v1/j1-jumbo/complete",
        headers={"Authorization": f"Bearer {os.environ['key']}"},
        json=params)

    return response.json()["completions"][0]["data"]["text"]

def tweet_thread(thread_name):
    print(thread_name + " starting")

    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # session = loop.run_until_complete(get_session())

    while True:
        try:
            # result = loop.run_until_complete(get_gpt(finetune_tweet, 1, 40, 1, session))
            # result = result.split("\n")[0].strip()

            # while result.strip() == "" or "!!" in result or "??" in result or "~~" in result or "_" in result or "**" in result:
            #     result = loop.run_until_complete(get_gpt(finetune_tweet, 1, 40, 1, session))
            #     result = result.split("\n")[0].strip()

            #     time.sleep(10)
            result = get_tweet()

            for i in range(3):
                if not is_bad(result, os.environ["PARALLELDOTS_KEY1"], False):
                    try:
                        twitter.update_status(result)
                    except:
                        traceback.print_exc()
                    break
                
                result = get_tweet()

            time.sleep(60 * 60)
        except Exception as e:
            print(e)
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

_thread.start_new_thread(reply_thread, ("reply thread", ))
_thread.start_new_thread(tweet_thread, ("tweet thread", ))

while 1:
    pass
