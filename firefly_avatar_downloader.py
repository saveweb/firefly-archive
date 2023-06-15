# {
#     "userInfoVO":{
#         "userId":326001,
#         "guid":"0dfb1e61-0486-454d-a5be-a4c90ff62715",
#         "anonymUser":false,
#         "userBase":{
#             "headPath":
import json
import os
import asyncio
import httpx

from itertools import count

def main():
    client = httpx.AsyncClient()
    client.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0",
        "Referer": "https://w.firefly.pub/post.html",
        "Origin": "https://w.firefly.pub",
    })
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for userId in range(0, 328 * 1000):
        json_filepath = f'uids/{userId//1000}/uid-{userId}.json'
        avatar_filepath = f'user_avatars/{userId//1000}/user-{userId}.avatar'
        if not os.path.exists(json_filepath):
            # print("userid %d not found" % userId, end='\r')
            continue
        if os.path.exists(avatar_filepath):
            continue
        with open(json_filepath, 'r', encoding='utf-8') as f:
            UserObj: dict = json.load(f)
        # print(f'userid {userId} parseing...', end='\r')
        userBase = UserObj['userInfoVO']['userBase']
        userBase: dict
        cors = []
        nickName = userBase['nickName']
        headPath = userBase['headPath']
        if headPath == "https://ugcfile.firefly.pub/defaultAvatar/defaultAvatar.png":
            continue
        print(userId, ':', headPath)
        loop.create_task(download_avatar(client, headPath, userId))
        while len(asyncio.all_tasks(loop)) > 8:
            loop.run_until_complete(asyncio.sleep(0.1))

    while len(asyncio.all_tasks(loop)) > 0:
        loop.run_until_complete(asyncio.sleep(1))

async def download_avatar(client: httpx.AsyncClient, headPath: str, userId: int):
    avatar_filepath = f'user_avatars/{userId//1000}/user-{userId}.avatar'
    while True:
        try:
            r = await client.get(headPath, timeout=60, follow_redirects=True)
            break
        except Exception:
            print("userid %d retrying" % userId, end='\r')
            await asyncio.sleep(1)
    if r.status_code != 200:
        print(r.status_code, headPath)
        return
    assert r.headers["Content-Length"] != "0"
    if 'image'  not in r.headers["Content-Type"]:
        print(r.headers["Content-Type"], headPath)
    os.makedirs(os.path.dirname(avatar_filepath), exist_ok=True)
    try:
        with open(avatar_filepath, 'wb') as f:
            f.write(r.content)
    except KeyboardInterrupt:
        os.remove(avatar_filepath)
        raise
if __name__ == "__main__":
    main()