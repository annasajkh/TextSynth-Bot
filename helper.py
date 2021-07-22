from pyppeteer import launch

import re
import asyncio
import tweepy

from profanity_check import predict
from better_profanity import profanity
import paralleldots
import os


paralleldots.set_api_key(os.environ["PARALLELDOTS_KEY"])


def build_text(status):
    text = re.sub("@[^\s]+", "", status.text)
    text = re.sub("https://[^\s]+", "", text).strip()
    text = re.sub("\n", " ", text)

    return f"{status.user.name}: {text}"


async def get_elemets(page):
	await page.waitForSelector("#input_text")

	input_text = await page.querySelector("#input_text")

	submit_button = await page.querySelector("#submit_button")

	return input_text, submit_button

async def get_GPTJ(text):
    browser, page, input_text, submit_button = await setup_browser()

    await input_text.type(text)
    await submit_button.click()

    gtext = await page.querySelector("#gtext")

    await asyncio.sleep(3)
    
    result = await page.evaluate("(element) => element.innerText",gtext)
    result = result.replace(text, "").strip().split("Bot:")[0].strip().split("\n")[0][0:280]

    await browser.close()

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

def reply(twitter, status, memory):

    name = status.user.screen_name

    if not name in memory.keys():
        memory[name] = []

    memory[name].append(build_text(status))

    if len(memory[name]) > 100:
        memory[name].pop(0)
    
    if len(memory.keys()) > 100000:
        del memory[memory.keys()[0]]
    
    text = "\n".join(memory[name]) + "\nBot: "

    print(text)

    print("-" * 30)

    try:
        result = asyncio.get_event_loop().run_until_complete(get_GPTJ(text))
    except:
        result = asyncio.get_event_loop().run_until_complete(get_GPTJ(text))

    while is_bad(result):
        try:
            result = asyncio.get_event_loop().run_until_complete(get_GPTJ(text))
        except:
            result = asyncio.get_event_loop().run_until_complete(get_GPTJ(text))

    memory[name].append(f"Bot: {result}")
    
    print(text + result)
    twitter.update_status(f"@{name} {result}", in_reply_to_status_id=status.id)