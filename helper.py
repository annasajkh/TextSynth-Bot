from pyppeteer import launch

import re
import asyncio
import random


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
    result = result.split("Bot:")[0].strip().split("\n")[0][0:280]
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