from os import error
import re
from traceback import print_exc
import traceback
from typing import Text
import requests

from profanity_check import predict
from better_profanity import profanity
import json
import re

import time
import random



url = "https://bellard.org/textsynth/api/v1/engines/gptj_6B/completions"

f = open("finetune.txt", "r")
finetune = f.read()
f.close()



def build_text(status):
    text = get_text(status)
    text = re.sub("@[^\s]+", "", text)
    text = re.sub("\n", " ", text).strip()
    
    return f"\n{text}"


def get_text(status):
    try:
        return status.extended_tweet["full_text"]
    except:
        return status.text


def get_gpt(text):

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

    for i in range(10):
        try:
            r = requests.post(url, data=json.dumps(payload, ensure_ascii=False), headers=headers)
            text = str(r.content, "utf-8", errors="replace")
            text = filter(lambda x: x != "",[chunk for chunk in text.split("\n")])
            text = "".join([json.loads(chunk)["text"] for chunk in text]).strip()

            break
        except Exception as e:
            print_exc()
            text = ""
            pass



    return text

def get_response(text):
    result = get_gpt(text)
    result = re.split("\n",result)[0].strip()[:280]
    result = re.sub("\n", " ", result)

    return result


def is_bad(text):
    if predict([text])[0] > 0.5 or profanity.contains_profanity(text):
        return True
    
    return False


def reply(twitter, status):
    if status.user.screen_name == "TextSynth":
        return
    
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
    
    text = finetune + "\n".join(memory) + "\n"

    print("make API requests")

    result = get_response(text)

    print(result)

    while is_bad(result):
        result = get_response(text)
        print(result)

    try:
        twitter.update_status(result, in_reply_to_status_id=reply_status.id, auto_populate_reply_metadata=True)
    except:
        traceback.print_exc()
