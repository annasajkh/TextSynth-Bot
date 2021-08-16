from traceback import print_exc
from profanity_check import predict
from better_profanity import profanity
from requests.sessions import session

import re
import traceback
import re
import json
import time
import random
import aiohttp
import os
import paralleldots

paralleldots.set_api_key(os.environ["PARALLELDOTS_KEY"])



url = "https://bellard.org/textsynth/api/v1/engines/gptj_6B/completions"

f = open("finetune.txt", "r")
finetune = f.read()
f.close()

f = open("finetune_tweet.txt", "r")
finetune_tweet = f.read()
f.close()
