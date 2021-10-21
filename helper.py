import asyncio
from setup import *
import requests
from alt_profanity_check import predict_prob

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


async def get_gpt(text, temperature, top_k, top_p, session : aiohttp.ClientSession):
    payload = {
        "prompt": text,
        "temperature": temperature,
        "top_k": top_k, 
        "top_p": top_p, 
        "seed": random.randrange(0, 10000)
    }

    if len(text) < 200:
        print(f"requesting text:\n{text}")
    else:
        print("requesting text...")

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

def get_response(text, memory, session, loop):
    result = loop.run_until_complete(get_gpt(text, 1.0, 40, 0.9, session))
    result = re.split(".*:",result)[0].strip()[:280]
    result = re.sub("\n", " ", result)

    for i in range(0, 20):
        print("checkking if there is something bad...")      

        if not is_bad(result) and result.strip() != "" and len(result) < 280 and result.strip() not in [chunk.split(":")[1].strip() for chunk in memory]:
            break
        
        result = loop.run_until_complete(get_gpt(text, 1.0, 40, 0.9, session))
        result = re.split(".*:",result)[0].strip()[:280]
        result = re.sub("\n", " s", result)

        time.sleep(2)
      
    return result


def is_bad(text):
    if predict_prob([text])[0] > 0.9:
        print("bad word")
        return True
    
    if True in [bad in text for bad in ["die", "kill", "burn body", "burn you"]]:
        print("kill word")
        return True
    
    return False



def reply(twitter, status, session, loop):
    time.sleep(2 + random.random() * 3)
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

        if len(statuses_cache) > 1000:
            statuses_cache.pop(0)

        time.sleep(2)

        index += 1
        if index > 10:
            break

    memory.reverse()
    memory = memory[:1000]

    text = finetune + "\n" + "\n".join(memory) + "\nTextSynth:"
    text = text.replace("User", reply_status.user.screen_name.replace(":", ""))

    print("make API requests")

    result = get_response(text, memory, session, loop)
    result = result[0:280]

    print("posting result...")

    try:
        updated_status = twitter.update_status(f"@{reply_status.user.screen_name} {result}", in_reply_to_status_id=reply_status.id)
        statuses_cache.append(updated_status)
    except Exception as e:
        updated_status = twitter.update_status(f"@{reply_status.user.screen_name} {str(e)}", in_reply_to_status_id=reply_status.id)
        statuses_cache.append(updated_status)
        traceback.print_exc()


async def get_session():
    return aiohttp.ClientSession()

def get_tweet():
    params = {
        "prompt": finetune_tweet_ai21,
        "numResults": 1,
        "maxTokens": 100,
        "stopSequences": ["#"],
        "topKReturn": 0,
        "temperature": 1.0
    }

    response = requests.post(
        "https://api.ai21.com/studio/v1/j1-jumbo/complete",
        headers={"Authorization": f"Bearer {os.environ['key']}"},
        json=params)

    return response.json()["completions"][0]["data"]["text"]