from traceback import print_exc
from requests.sessions import session

import re
import traceback
import re
import json
import time
import random
import aiohttp
import os

os.system("pip3 install scikit-learn==0.24.0")

url = "https://bellard.org/textsynth/api/v1/engines/gptj_6B/completions"
statuses_cache = []


f = open("finetune.txt", "r")
finetune = f.read()
f.close()

f = open("finetune_tweet.txt", "r")
finetune_tweet = f.read()
f.close()

finetune_tweet_ai21 = """
tweet: if anyone feels like getting a snack after this shit post please do#
tweet: i've lost faith in my own opinions#
tweet: wtf? i just farted#
tweet: the rain is pretty but i don't wanna go outside and be wet#
tweet: i was doing dishes when i accidentally dropped the bowl, hard!#
tweet:
""".strip()