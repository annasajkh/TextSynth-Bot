import re
from traceback import print_exc
import traceback

from profanity_check import predict
from better_profanity import profanity
import json
import re

import time
import random
import aiohttp
from requests.sessions import session



url = "https://bellard.org/textsynth/api/v1/engines/gptj_6B/completions"

f = open("finetune.txt", "r")
finetune = f.read()
f.close()

async def get_session():
    return aiohttp.ClientSession()
