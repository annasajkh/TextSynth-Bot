import asyncio
from setup import *
import requests
from alt_profanity_check import predict_prob

def build_text(status):
    text = get_text(status)
    text_temp = ""

    include = False
    
    for chunk in text.split(" "):
        if "@" not in chunk:
            include = True
        if include:
           text_temp += chunk + " "

    text = text_temp.strip()

    text = re.sub("https://[^\s]+", "", text)
    text = re.sub("\n", " ", text).strip()

    name = status.user.screen_name.replace(":", "")

    return f"{name}: {text}"


def get_text(status):
    try:
        return status.extended_tweet["full_text"]
    except:
        return status.text

def get_gpt2(text):

    if len(text) < 1000:
        print(text)

    payload = {
        "prompt": text,
        "temperature": 0.8,
        "top_k": 40, 
        "top_p": 1.0,
        "seed": 0,
        "max_tokens": 200,
        "stop": "\n"
    }

    headers= {
        "Authorization": os.environ["TEXTSYNTH_KEY"]
    }

    resp = requests.post("https://api.textsynth.com/v1/engines/gptj_6B/completions",data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), headers=headers)

    print(resp.text)

    return json.loads(resp.text)["text"]


def get_gpt(text):
    params = {
      "text": text,
      "length": 80,
      "repetition_penalty": 1.0,
      "temperature": 0.5,
      "top_p": 1,
      "top_k": 40,
      "stop_sequences": '["\\n"]',
      "authorization": os.environ["HELLOFOREFRONT_KEY"]
    }


    result = requests.get("https://demo-playground.forefront.link", params=params)
    result = result.text.split("event: update")[-1].split("retry: 30000")[0].replace("data: ", "").split(":")[-1].strip()

    for i in range(5):
      if not is_bad(result):
        break
      
      result = requests.get("https://demo-playground.forefront.link", params=params)
      result = result.text.split("event: update")[-1].split("retry: 30000")[0].replace("data: ", "").split(":")[-1].strip()

      if i == 4:
        return "i'm sorry i don't know"
      
      time.sleep(5)

    return result

def get_response(text, reply_text, memory):
    # try:
    #     result = get_gpt(text)
    # except Exception as e:
    #     print_exc()
    
    result = get_gpt2(text)
    result = re.split(".*:",result)[0].strip()[:280]
    result = re.sub("\n", " ", result)
    
    
    # while result.strip() == "":
    #     result = get_gpt2(text)
    #     result = re.split(".*:",result)[0].strip()[:280]
    #     result = re.sub("\n", " ", result)
    #     time.sleep(2)
    
    print(f"RESULT: {result}")

    for i in range(0, 20):
        print("checkking if there is something bad...")

        if not is_bad(result) and result.strip().lower() not in [chunk.split(":")[1].strip().lower() for chunk in memory] and result.strip().lower != reply_text.strip().lower() and len(result.strip()) <= 280 and len(result.strip()) > 0:
            break
        
        # try:
        #     result = get_gpt(text)
        # except Exception as e:
        #     print_exc()
        
        result = get_gpt2(text)
        result = re.split(".*:",result)[0].strip()
        result = re.sub("\n", " ", result)
        
        # while result.strip() == "":
        #     result = get_gpt2(text)
        #     result = re.split(".*:",result)[0].strip()[:280]
        #     result = re.sub("\n", " ", result)
        #     time.sleep(2)

        print(f"RESULT: {result}")

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



def reply(twitter, status):
    time.sleep(1 + random.random() * 2)
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
    memory = memory[:30]

    text = finetune + "\n" + "\n".join(memory) + "\nTextSynth:"
    #text = text.replace("User", reply_status.user.screen_name)

    print("make API requests")

    result = get_response(text, get_text(reply_status) ,memory)
    result = result[0:280]

    print("posting result...")
    
    for i in range(20):
        try:
          temp = [""]
    
          for chunk in result.split(" "):
            if len(temp[-1] + " " + chunk) > 280:
              temp[-1] = temp[-1].strip()
              temp.append("")
            
            temp[-1] += " " + chunk
          
          if temp[0].strip() != "":
            tweet = twitter.update_status(f"@{reply_status.user.screen_name} {temp[0]}", in_reply_to_status_id=reply_status.id)
            statuses_cache.append(tweet)
    
            for i in range(1, len(temp)):
              time.sleep(random.random() * 3 + 1)
    
              tweet = twitter.update_status(status=temp[i], 
                                            in_reply_to_status_id=tweet.id,
                                            auto_populate_reply_metadata=True)
              statuses_cache.append(tweet)
            break
        except Exception as e:
            print(e)
            time.sleep(5)


async def get_session():
    return aiohttp.ClientSession()

def get_tweet():
    params = {
        "prompt": finetune_tweet_ai21,
        "numResults": 1,
        "maxTokens": 100,
        "stopSequences": ["#"],
        "topKReturn": 0,
        "temperature": 0.8
    }

    response = requests.post(
        "https://api.ai21.com/studio/v1/j1-jumbo/complete",
        headers={"Authorization": f"Bearer {os.environ['key']}"},
        json=params)

    return response.json()["completions"][0]["data"]["text"].replace("tweet: ", "")