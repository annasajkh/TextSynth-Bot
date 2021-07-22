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

        twitter.create_favorite(status.id)

        name = status.user.screen_name

        if not name in memory.keys():
            memory[name] = []

        memory[name].append(build_text(status))

        if len(memory[name]) > 100:
            memory[name].pop(0)
        
        if len(memory.keys()) > 100000:
            del memory[memory.keys()[0]]
        
        text = "\n".join(memory[name]) + "\nBot: "


        
        try:
            result = asyncio.get_event_loop().run_until_complete(get_GPTJ(text))
        except:
            result = asyncio.get_event_loop().run_until_complete(get_GPTJ(text))
        
        while result in "\n".join(memory[name]):
            result = asyncio.get_event_loop().run_until_complete(get_GPTJ(text))

        while is_bad(result):
            try:
                result = asyncio.get_event_loop().run_until_complete(get_GPTJ(text))

                while result in "\n".join(memory[name]):
                    result = asyncio.get_event_loop().run_until_complete(get_GPTJ(text))
            except:
                result = asyncio.get_event_loop().run_until_complete(get_GPTJ(text))

                while result in "\n".join(memory[name]):
                    result = asyncio.get_event_loop().run_until_complete(get_GPTJ(text))

        memory[name].append(f"Bot: {result}")
        
        print("-" * 30)
        print(text + result)
        print("-" * 30)
        
        twitter.update_status(result, in_reply_to_status_id=status.id, auto_populate_reply_metadata=True)

    def on_error(self, status_code):
        if status_code == 420:
            print("ahhhh")
            return False
        
        print(status_code)


stream = tweepy.Stream(auth, Listener())


while True:
    try:
        try:
            stream.filter(track=["@TextSynth"], is_async=True)
        except:
            pass
        try:
            result = asyncio.get_event_loop().run_until_complete(get_GPTJ(""))

            while is_bad(result):
                try:
                    result = asyncio.get_event_loop().run_until_complete(get_GPTJ(""))
                except:
                    result = asyncio.get_event_loop().run_until_complete(get_GPTJ(""))
                    
            twitter.update_status(result)
        except:
            pass
        time.sleep(60 * 60)
    except Exception as e:
        traceback.print_exc()
        time.sleep(10)