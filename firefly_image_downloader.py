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
    sub_dir_start = int(input("sub dir start: "))
    sub_dir_end = int(input("sub dir end: "))
    for postid in range(sub_dir_start * 1000 - 100, sub_dir_end * 1000 + 100):
        if postid//1000 < sub_dir_start:
            continue
        if postid//1000 > sub_dir_end:
            break
        sub_dir = postid//1000
        if not os.path.exists(f'posts/{sub_dir}/post-{postid}.json'):
            print("postid %d not found" % postid, end='\r')
            continue
        with open(f'posts/{sub_dir}/post-{postid}.json', 'r', encoding='utf-8') as f:
            post: dict = json.load(f)
        print(f'postid {postid} downloading...')
        for block in post.get('blocks', []):
            block: dict
            cors = []
            if block.get('image') is not None:
                if block['image'].get('url') is not None:
                    cor = download_media(client, block['image']['url'], postid)
                    cors.append(cor)
            if block.get('video') is not None:
                if block['video'].get('url') is not None:
                    cor = download_media(client, block['video']['url'], postid)
                    cors.append(cor)
                if block['video'].get('coverUrl') is not None:
                    cor = download_media(client, block['video']['coverUrl'], postid)
                    cors.append(cor)
            for cor in cors:
                loop.create_task(cor)
        while len(asyncio.all_tasks(loop)) > 8:
            loop.run_until_complete(asyncio.sleep(0.1))

    while len(asyncio.all_tasks(loop)) > 0:
        loop.run_until_complete(asyncio.sleep(1))

async def download_media(client: httpx.AsyncClient, url: str, postid: int):
    filepath = f'posts_media/{postid//1000}/post-{postid}/{url.split("?")[0].split("/")[-1]}'
    if os.path.exists(filepath):
        return
    while True:
        try:
            r = await client.get(url, timeout=60)
            break
        except Exception:
            print("postid %d retrying" % postid, end='\r')
            await asyncio.sleep(1)
    if r.status_code == 404:
        print('404', url)
        return
    assert r.status_code == 200
    assert r.headers["Content-Length"] != "0"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        with open(filepath, 'wb') as f:
            f.write(r.content)
    except KeyboardInterrupt:
        os.remove(filepath)
        raise
if __name__ == "__main__":
    main()