import asyncio
from setup import *


def build_text(status):
    text = get_text(status)
    text = re.sub("@[^\s]+", "", text)
    text = re.sub("https://[^\s]+", "", text)
    text = re.sub("\n", " ", text).strip()

    name = status.user.screen_name.replace(":", "")

    return f"{name}: {text}"


def get_text(status):
    try:
        return status.extended_tweet["full_text"]
    except:
        return status.text


async def get_gpt(text, session : aiohttp.ClientSession):

    payload = {
        "prompt": text,
        "temperature": 0.8,
        "top_k": 20, 
        "top_p": 0.9, 
        "seed": random.randrange(0, 10)
    }

    print(f"requesting text:\n{text}")

    text = ""

    try:
        async with session.post(url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8")) as response:
            try:
                text = await response.text()
            except:
                try:
                    text = await response.content.read()
                    text = str(text,response.get_encoding(),errors="replace")
                except:
                    text = await response.content.read()
                    text = str(text,"utf-8",errors="replace")
                    
            text = filter(lambda x: x != "",[chunk for chunk in text.split("\n")])
            text = "".join([json.loads(chunk)["text"] for chunk in text]).strip()
    except Exception as e:
        print_exc()
        pass

    return text

def get_response(text, session, loop):
    result = loop.run_until_complete(get_gpt(text, session))
    result = re.split(".*:",result)[0].strip()[:280]
    result = re.sub("\n", " ", result)

    for i in range(0, 20):
        if not is_bad(result) and result.strip() != "":
            break
        
        result = loop.run_until_complete(get_gpt(text, session))
        result = re.split(".*:",result)[0].strip()[:280]
        result = re.sub("\n", " ", result)

        time.sleep(1)



    return result


def is_bad(text):
    if predict([text])[0] == 1 or profanity.contains_profanity(text):
        print("profinaty check it's bad word")
        return True
    
    try:
        result = paralleldots.abuse(text)

        if result["abusive"] == 1:
            print("paralleldots thinks it's bad word")
            return True
    except:
        return False
    
    return False



def reply(twitter, status, session, loop):

    if "rt" in get_text(status).lower():
        return

    try:
        twitter.create_favorite(status.id)
    except:
        return

    memory = []

    reply_status = status

    index = 0

    memory.append(build_text(status))

    while status.in_reply_to_status_id != None:

        try:
            for status_cache in statuses_cache:
                if status_cache.id == status.in_reply_to_status_id:
                    memory.append(build_text(status_cache))
                    status = status_cache
                    raise Exception("alternative for continue outer loop")
        except:
            continue

        try:
            status = twitter.get_status(status.in_reply_to_status_id)
        except:
            break

        text = build_text(status)
        memory.append(text)

        statuses_cache.append(status)

        if len(statuses_cache) > 100000:
            statuses_cache.pop(0)

        time.sleep(2)

        index += 1
        if index > 10:
            break

    memory.reverse()
    memory = memory[:5000]

    text = finetune + "\n" + "\n".join(memory) + "\nTextSynth:"
    text = text.replace("User", reply_status.user.screen_name.replace(":", ""))

    print("make API requests")

    result = get_response(text, session, loop)
    result = result[0:280]

    try:
        updated_status = twitter.update_status(f"@{reply_status.user.screen_name} {result}", in_reply_to_status_id=reply_status.id)
        statuses_cache.append(updated_status)
    except Exception as e:
        updated_status = twitter.update_status(f"@{reply_status.user.screen_name} {str(e)}", in_reply_to_status_id=reply_status.id)
        statuses_cache.append(updated_status)
        traceback.print_exc()


async def get_session():
    return aiohttp.ClientSession()
