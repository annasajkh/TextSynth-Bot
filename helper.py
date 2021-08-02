import asyncio
from setup import *


def build_text(status):
    text = get_text(status)
    text = re.sub("@[^\s]+", "", text)
    text = re.sub("\n", " ", text).strip()

    name = status.user.screen_name.replace(":", "").capitalize()

    return f"{name}: {text}"


def get_text(status):
    try:
        return status.extended_tweet["full_text"]
    except:
        return status.text


async def get_gpt(text, session : aiohttp.ClientSession):

    payload = {
        "prompt": text,
        "temperature": 1,
        "top_k": 40, 
        "top_p": 0.9, 
        "seed": 0
    }

    print(f"requesting text:\n{text}")

    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    text = ""

    for i in range(10):
        try:
            async with session.post(url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), headers=headers) as response:
                
                try:
                    text = await response.text()
                except:
                    try:
                        text = await response.text(errors="ignore")
                    except:
                        text = await response.text(errors="replace")
                        
                text = filter(lambda x: x != "",[chunk for chunk in text.split("\n")])
                text = "".join([json.loads(chunk)["text"] for chunk in text]).strip()
                
                if text.strip() == "":
                    continue
        except Exception as e:
            print_exc()
            pass



    return text

async def get_response(text, session):
    result = await get_gpt(text, session)
    result = re.split(".*?:",result)[0].strip()[:280]
    result = re.sub("\n", " ", result)

    return result


def is_bad(text):
    if predict([text])[0] > 0.9 or profanity.contains_profanity(text):
        return True
    
    try:
        result = paralleldots.abuse(text)

        if result["abusive"] > 0.9:
            return True
    except:
        return False
    
    return False


async def reply(twitter, status, session):
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
        time.sleep(2)
        
        index += 1
        if index > 10:
            break
    
    memory.reverse()
    
    text = finetune + "\n" + "\n".join(memory) + "\nTextSynth:"

    print("make API requests")

    result = await get_response(text, session)

    print(result)

    while is_bad(result):
        result = await get_response(text, session)
        print(result)

    try:
        twitter.update_status(result, in_reply_to_status_id=reply_status.id, auto_populate_reply_metadata=True)
    except Exception as e:
        twitter.update_status(str(e), in_reply_to_status_id=reply_status.id, auto_populate_reply_metadata=True)
        traceback.print_exc()

async def get_session():
    return aiohttp.ClientSession()
