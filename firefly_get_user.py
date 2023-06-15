import json
import os
import asyncio
import httpx


def main():
    client = httpx.AsyncClient()
    client.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0",
        "Referer": "https://w.firefly.pub/post.html",
        "Content-Type": "application/json",
        "Origin": "https://w.firefly.pub",
    })
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for userId in range(0, 588488):

        if os.path.exists(f'uids/{userId//1000}/uid-{userId}.json'):
            print("uid %d found (local json file)" % userId, end='\r')
            continue
        while len(asyncio.all_tasks(loop)) > 20:
            loop.run_until_complete(asyncio.sleep(0.1))

        loop.create_task(download_user_info(client, userId))
    while len(asyncio.all_tasks(loop)) > 0:
        loop.run_until_complete(asyncio.sleep(1))
        
async def download_user_info(client: httpx.AsyncClient, userId: int):
        data = {"data":{"userId":userId},
                "servicePath":"/game/app/user/personal-homepage",
                "httpType":"post"
        }
        data_str = json.dumps(data, separators=(',', ':'))
        while True:
            try:
                r = await client.post("https://w.firefly.pub/queryData", data=data_str, timeout=60)
                break
            except Exception:
                print("uid %d retrying" % userId, end='\r')
                await asyncio.sleep(1)
            
        respobj = r.json()
        assert respobj["code"] == 200
        if respobj["data"]["code"] != 200:
            print(userId, respobj['data']['msg'], end='\r')
            return
        if respobj["data"]["data"] is None:
            print("uid %d not found" % userId, end='\r')
            return
        UserObj = respobj["data"]["data"]
        print("uid %d downloaded" % userId, end='\r')
        await save_user(UserObj)


async def save_user(UserObj):
    userId = int(UserObj['userInfoVO']['userId'])
    os.makedirs(f'uids/{userId//1000}', exist_ok=True)
    try:
        with open(f'uids/{userId//1000}/uid-{userId}.json', 'w' ,encoding='utf-8') as f:
            json.dump(UserObj, f, indent=4, ensure_ascii=False, separators=(',', ':'))
    except:
        os.remove(f'uids/{userId//1000}/uid-{userId}.json')

if __name__ == "__main__":
    main()
