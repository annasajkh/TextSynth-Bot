from pyppeteer import launch

import re
import asyncio
import random


from profanity_check import predict
from better_profanity import profanity
import paralleldots
import os
import re

import time

paralleldots.set_api_key(os.environ["PARALLELDOTS_KEY"])


def build_text(status):
    text = get_text(status)
    text = re.sub("https://[^\s]+", "", text).strip()
    text = re.sub("\n", " ", text)

    return f"{status.user.screen_name}: {text}"

def get_text(status):
    try:
        return status.extended_tweet["full_text"]
    except:
        return status.text

async def get_elemets(page):
	await page.waitForSelector("#input_text")

	input_text = await page.querySelector("#input_text")

	submit_button = await page.querySelector("#submit_button")

	return input_text, submit_button

async def get_gpt(text):
    browser, page, input_text, submit_button = await setup_browser()

    await input_text.type(text)
    await submit_button.click()

    gtext = await page.querySelector("#gtext")

    await asyncio.sleep(random.randrange(3, 5))
    
    result = await page.evaluate("(element) => element.innerText",gtext)

    await browser.close()

    return result.replace(text, "").strip()


async def get_response(text):
    result = await get_gpt(text)
    result = re.split(".*?:",result)[0].strip()
    return result


async def setup_browser():
    browser = await launch({"args":["--no-sandbox","--disable-setuid-sandbox"]})
    page = await browser.newPage()

    await page.goto("https://bellard.org/textsynth/")

    input_text, submit_button = await get_elemets(page)

    return browser, page, input_text, submit_button


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


def reply(twitter, status):
    if status.favorited:
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