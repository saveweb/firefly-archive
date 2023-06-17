import json
import os
import asyncio
import httpx


def main():
    client = httpx.AsyncClient()
    client.headers.update({
        "code": "200",
        "Authorization": "Bearer 993eef9f-80dd-4e82-88ee-05ff733e866b",
        "DeviceUUID": "6336054e-a787-42fd-8105-44b1b5c9e6e4",
        "Version": "2.2.3",
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "okhttp/4.10.0",
    })
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for userId in range(82000, 326374):
        print("userId %d" % userId)
        while len(asyncio.all_tasks(loop)) > 20:
            loop.run_until_complete(asyncio.sleep(0.1))

        loop.create_task(sub_user(client, userId))
    while len(asyncio.all_tasks(loop)) > 0:
        loop.run_until_complete(asyncio.sleep(1))
        
async def sub_user(client: httpx.AsyncClient, userId: int):
        data = {"data":{"sourceId":userId,
                        "sourceType":3,
                        "type":1,
                    }
        }
        data_str = json.dumps(data, separators=(',', ':'))
        while True:
            try:
                r = await client.post("https://api.firefly.pub/yinghuo/gateway/game/app/user/collection/subscribe", data=data_str, timeout=60)
                break
            except Exception:
                print("userId %d retrying" % userId, end='\r')
                await asyncio.sleep(1)
            
        respobj = r.json()
        if respobj["code"] == 500:
            print(userId, "用户不存在")

        print(respobj)

if __name__ == "__main__":
    main()