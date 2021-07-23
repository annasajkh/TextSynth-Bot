from dotenv import load_dotenv
load_dotenv()

import time
import traceback

from twitter_api import *
from helper import *


class Listener(tweepy.StreamListener):
    def on_status(self, status):
        if status.user.screen_name == "TextSynth":
            return

        twitter.create_favorite(status.id)

        memory = []

        reply_status = status

        index = 0

        memory.append(build_text(status))

        while status.in_reply_to_status_id != None:
            status = twitter.get_status(status.in_reply_to_status_id)
            memory.append(build_text(status))

            time.sleep(1)
            
            index += 1
            if index > 10:
                break
        
        memory.reverse()
        

        text = "\n".join(memory) + "\nTextSynth: "

        
        try:
            result = asyncio.get_event_loop().run_until_complete(get_response(text))
        except:
            result = asyncio.get_event_loop().run_until_complete(get_response(text))
        
        while result in "\n".join(memory):
            result = asyncio.get_event_loop().run_until_complete(get_response(text))


        while is_bad(result):
            try:
                result = asyncio.get_event_loop().run_until_complete(get_response(text))

                while result in "\n".join(memory):
                    result = asyncio.get_event_loop().run_until_complete(get_response(text))
            except:
                result = asyncio.get_event_loop().run_until_complete(get_response(text))

                while result in "\n".join(memory):
                    result = asyncio.get_event_loop().run_until_complete(get_response(text))
        
        print("-" * 30)
        print(text + result)
        print("-" * 30)
        
        twitter.update_status(result, in_reply_to_status_id=reply_status.id, auto_populate_reply_metadata=True)

    def on_error(self, status_code):
        if status_code == 420:
            print("ahhhh")
            return False
        
        print(status_code)


stream = tweepy.Stream(auth, Listener())


while True:
    try:
        stream.filter(track=["@TextSynth", "talk with ai", "self aware", ""])
    except Exception as e:
        traceback.print_exc()
        time.sleep(10)