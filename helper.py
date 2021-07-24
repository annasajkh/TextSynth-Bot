import re
import asyncio
import aiohttp

from profanity_check import predict
from better_profanity import profanity
import paralleldots
import os
import json
import re

import time
import random
import traceback

paralleldots.set_api_key(os.environ["PARALLELDOTS_KEY"])


url = "https://bellard.org/textsynth/api/v1/engines/gptj_6B/completions"

def html_escape(text)
    r = "";

    for c in tex.split(""):
        if c == "<":
            r += "&lt;"
        elif c == ">":
            r += "&gt;"
        elif c == "&":
            r += "&amp;"
        elif c == "\"":
            r += "&quot;"
        else:
            r += c;
        
    return r;


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
        "prompt": text.encode("utf-8").decode("utf-8").ignore,
        "temperature": 1.2,
        "top_k": 20, 
        "top_p": 0.8, 
        "seed": 0,
        "stream": True
    }

    headers = {
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url,data=json.dumps(payload), headers=headers) as response:
            text = await response.text()


    text = [chunk for chunk in text.split("\n\n")]
    print(list(text))
    text = "".join([json.loads(chunk)["text"] for chunk in text]).strip()

    return html_escape(text)

async def get_response(text):
    result = await get_gpt(text)
    result = re.split(".*?:",result)[0].strip()[:280]
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

    result = await get_response(text)

    while is_bad(result):
        result = await get_response(text)
    
    print("-" * 30)
    print(text + result)
    print("-" * 30)
    
    twitter.update_status(result, in_reply_to_status_id=reply_status.id, auto_populate_reply_metadata=True)