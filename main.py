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

        name = status.user.screen_name

        if not name in memory.keys():
            memory[name] = []

        memory[name].append(build_text(status))

        if len(memory[name]) > 100:
            memory[name].pop(0)
        
        text = "\n".join(memory[name]) + "\nBot: "
        
        print(text)

        print("-" * 30)

        result = asyncio.get_event_loop().run_until_complete(get_GPTJ(text))

        while is_bad(result):
            result = asyncio.get_event_loop().run_until_complete(get_GPTJ(text))

        memory[name].append(f"Bot: {result}")
        
        print(text + result)
        twitter.update_status(result, in_reply_to_status_id=status.id, auto_populate_reply_metadata=True)

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
        traceback.print_exception()
        time.sleep(10)