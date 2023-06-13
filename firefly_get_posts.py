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
    skipids = read_skipids()
    max_post_id = find_max_post_id()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    sub_dir_start = int(input("sub dir start: "))
    sub_dir_end = int(input("sub dir end: "))
    start_post_id = sub_dir_start * 1000
    for postid in range(start_post_id, 588488+5000):
        if postid//1000 < sub_dir_start:
            continue
        if postid//1000 > sub_dir_end:
            break
        if postid in skipids:
            print("postid %d skipped" % postid, end='\r')
            continue
        if os.path.exists(f'posts/{postid//1000}/post-{postid}.json'):
            print("postid %d found (local json file)" % postid, end='\r')
            continue
        while len(asyncio.all_tasks(loop)) > 20:
            loop.run_until_complete(asyncio.sleep(0.1))

        loop.create_task(download_post(client, postid))
    while len(asyncio.all_tasks(loop)) > 0:
        loop.run_until_complete(asyncio.sleep(1))
        
async def download_post(client: httpx.AsyncClient, postid: int):
        data = {"data":{"postId":postid},
                "servicePath":"/game/post/app/detail",
                "httpType":"post"
        }
        data_str = json.dumps(data, separators=(',', ':'))
        while True:
            try:
                r = await client.post("https://w.firefly.pub/queryData", data=data_str, timeout=60)
                break
            except Exception:
                print("postid %d retrying" % postid, end='\r')
                await asyncio.sleep(1)
            
        respobj = r.json()
        assert respobj["code"] == 200
        assert respobj["data"]["code"] == 200, respobj['data']['msg']
        if respobj["data"]["data"] is None:
            print("postid %d not found" % postid, end='\r')
            return
        post = respobj["data"]["data"]
        print("postid %d downloaded" % postid)
        await save_post(post)

def find_max_post_id():
    max_post_id = 0
    max_sub_dir_int = 0
    for sub_dir in os.listdir('posts'):
        if sub_dir.isdigit():
            max_sub_dir_int = max(max_sub_dir_int, int(sub_dir))
    for name_in_sub_dir in os.listdir(f'posts/{max_sub_dir_int}'):
        if name_in_sub_dir.endswith('.json'):
            post_id = int(name_in_sub_dir.split('.')[0].split('-')[-1])
            max_post_id = max(max_post_id, post_id)
    if max_post_id > 1:
        max_post_id -= 100
    return max_post_id

async def save_post(post):
    postid = post['postId']
    with open(f'posts/post-{postid}.json', 'w') as f:
        json.dump(post, f, indent=4, ensure_ascii=False, separators=(',', ':'))
    move_to_sub_dir(postid)

def read_skipids():
    skipids = set()
    with open('skipids.txt', 'r') as f:
        skipids.update(int(line.strip()) for line in f.readlines())
    return skipids



def move_all_to_sub_dir():
    for file in os.listdir('posts'):
        if file.endswith('.json'):
            print(file)
            post_id = file.split('.')[0].split('-')[-1]
            post_id = int(post_id)
            move_to_sub_dir(post_id)

def move_to_sub_dir(postid: int):
    os.makedirs(f'posts/{postid//1000}', exist_ok=True)
    os.rename(f'posts/post-{postid}.json', f'posts/{postid//1000}/post-{postid}.json')

if __name__ == "__main__":
    main()