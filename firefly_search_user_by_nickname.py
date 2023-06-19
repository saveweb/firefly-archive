import rich
import json
import os


def search_nickName_in_posts(query: str):
    matched_nickName = {}
    for postid in range(0, 592240):
        if postid % 1000 == 0:
            print(f'..{postid}..', end='\r')
        sub_dir = postid//1000
        json_path = f'posts/{sub_dir}/post-{postid}.json'
        if not os.path.exists(json_path):
            # print("%d not found" % postid, end='\r')
            continue
        with open(json_path, 'r', encoding='utf-8') as f:
            post: dict = json.load(f)
        userId = post['userId']
        nickName = post['nickName']
        if query in nickName:
            print(userId, nickName)
            if userId not in matched_nickName:
                matched_nickName[userId] = nickName
    
    print("== Done ==")
    rich.print(matched_nickName)


# userInfoVO
#   userBase
#       nickName
#       personDesc
def search_nickName_in_uids(query: str):
    matched_nickName = {}
    for uid in range(0, 328000):
        if uid % 1000 == 0:
            print(f'..{uid}..', end='\r')
        sub_dir = uid//1000
        json_path = f'uids/{sub_dir}/uid-{uid}.json'
        if not os.path.exists(json_path):
            continue
        with open(json_path, 'r', encoding='utf-8') as f:
            user: dict = json.load(f)
        if uid not in matched_nickName:
            matched_nickName[uid] = [
                user['userInfoVO']['userBase']['nickName'],
                user['userInfoVO']['userBase']['personDesc']
            ]
    rich.print(matched_nickName)


if __name__ == '__main__':
    # search_nickName_in_posts(query=input('Search NickName: '))
    search_nickName_in_uids(query=input('Search NickName: '))