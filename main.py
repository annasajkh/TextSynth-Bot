from dotenv import load_dotenv
load_dotenv()

import time
import traceback
import asyncio

from twitter_api import *
from helper import *

dril_gpt2 = twitter.get_user("dril_gpt2").id_str
make_up_a_guy_gpt = twitter.get_user("gpt2upaguy").id_str
deep_leffen = twitter.get_user("DeepLeffen").id_str
text_synth = twitter.get_user("TextSynth").id_str
    
class Listener(tweepy.StreamListener):
    def on_status(self, status):

        if status.user.screen_name == "TextSynth":
            return

        asyncio.get_event_loop().run_until_complete(reply(twitter, status))

        if random.random() > 0.99:
            text = asyncio.get_event_loop().run_until_complete(get_gpt(finetune + "\nBot: "))
            text = re.split(".*?:",text)[0].strip()[:280]

            twitter.update_status(text)


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
        stream.filter(track=["@TextSynth"], follow=[dril_gpt2, make_up_a_guy_gpt, deep_leffen, text_synth])
    except Exception as e:
        traceback.print_exc()
        time.sleep(10)
