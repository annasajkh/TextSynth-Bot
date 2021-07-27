import re
import aiohttp

from profanity_check import predict
from better_profanity import profanity
import paralleldots
import os
import json
import re

import time
import random

paralleldots.set_api_key(os.environ["PARALLELDOTS_KEY"])


url = "https://bellard.org/textsynth/api/v1/engines/gptj_6B/completions"

f = open("finetune.txt", "r")
finetune = f.read()
f.close()
session = aiohttp.ClientSession()



def build_text(status):
    text = get_text(status)
    text = re.sub("https://[^\s]+", "", text)
    text = re.sub("@[^\s]+", "", text)
    text = re.sub("\n", " ", text).strip()
    
    return f"{status.user.screen_name}: {text}"


def get_text(status):
    try:
        return status.extended_tweet["full_text"]
    except:
        return status.text


async def get_gpt(text):

    payload = {
        "prompt": text,
        "temperature": 1,
        "top_k": 40, 
        "top_p": 0.9, 
        "seed": 0
    }

    headers = {
        "Content-Type": "application/json"
    }

    while True:
        async with session.post(url,data=json.dumps(payload, ensure_ascii=False), headers=headers) as response:
            text = await response.text()
            
            try:
                text = filter(lambda x: x != "",[chunk for chunk in text.split("\n")])
                text = "".join([json.loads(chunk)["text"] for chunk in text]).strip()

                if "??" in text or "!!" in text or "**" in text or len(text) < 20:
                    continue

                break
            except:
                pass



    return text

async def get_response(text):
    result = await get_gpt(text)
    result = re.split(".*?:",result)[0].strip()[:280]
    result = re.sub("\n", " ", result)

    return result


def is_bad(text):
    if predict([text])[0] > 0.5 or profanity.contains_profanity(text):
        return True
    
    try:
        result = paralleldots.abuse(text)

        if result["abusive"] > 0.5:
            return True
    except:
        return False
    
    return False


async def reply(twitter, status):
    time.sleep(random.uniform(0,2))

    try:
        twitter.create_favorite(status.id)
    except:
        return

    memory = []

    reply_status = status

    index = 0

    memory.append(build_text(status))

    while status.in_reply_to_status_id != None:
        status = twitter.get_status(status.in_reply_to_status_id)
        memory.append(build_text(status))

        try:
            twitter.create_favorite(status.id)
        except:
            pass

        time.sleep(1)
        
        index += 1
        if index > 10:
            break
    
    memory.reverse()
    
    text = finetune + "\n".join(memory) + "\nBot: "

    result = await get_response(text)

    while is_bad(result):
        result = await get_response(text)

    while True:
        try:
            twitter.update_status(result, in_reply_to_status_id=reply_status.id, auto_populate_reply_metadata=True)
            break
        except:
            result = await get_response(text)

            while is_bad(result):
                result = await get_response(text)
