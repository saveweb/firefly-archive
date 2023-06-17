import json
import os
import shutil
import sys
import time
import rich
from dataclasses import dataclass

@dataclass
class Post:
    postid: int
    userId: int
    nickName: str
    
    postType: int
    # 1: 一般文字
    postLabelList: list

    likeCount: int
    commentCount: int
    shareCount: int
    favCount: int

    title: str
    publishTime: int
    publishTime_str: str
    tagList: list
    blocks: list[dict]
    hotCommentList: list

    gameInfoVo: dict = None
    diaryVo: dict = None
    def __init__(self, post: dict):
        self.postid: int = post['postId']
        self.userId: int = post['userId']
        self.nickName: str = post['nickName']

        self.postType: int = post['postType']
        self.postLabelList: list = post['postLabelList']

        self.likeCount: int = post['likeCount']
        self.commentCount: int = post['commentCount']
        self.shareCount: int = post['shareCount']
        self.favCount: int = post['favCount']

        
        self.title: str = post['title']
        self.publishTime: int = post['publishTime'] / 1000
        self.publishTime_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.publishTime))
        self.tagList: list = post['tagList']
        self.blocks: list[dict] = post['blocks']
        self.hotCommentList: list = post['hotCommentList']

        self.gameInfoVo: dict = post['gameInfoVo']
        self.diaryVo: dict = post['diaryVo']


def main():
    userId_toSearch = 158828
    userId_to_postids_map = load_user_posts_map()
    postids = userId_to_postids_map[f"{userId_toSearch}"]
    avatar_filepath = f'user_avatars/{userId_toSearch//1000}/user-{userId_toSearch}.avatar'

    for postid in postids:

        sub_dir = postid//1000
        json_path = f'posts/{sub_dir}/post-{postid}.json'
        if not os.path.exists(json_path):
            # print("%d not found" % postid, end='\r')
            continue
        with open(json_path, 'r', encoding='utf-8') as f:
            post: dict = json.load(f)
        
        if not post['userId'] == userId_toSearch:
            continue

        # hotCommentList = post["hotCommentList"] # 26445

        # print('===',postid, '===')
        gen_post_archive(post)
    print(f"=== {len(postids)} end ===")

def load_user_posts_map():
    with open('map_userId_to_postid.json', 'r', encoding='utf-8') as f:
        map_userId_to_postid: dict = json.load(f)
    return map_userId_to_postid

def map_users_posts():
    map_userId_to_postid = {}
    for postid in range(0, 592240):
        sub_dir = postid//1000
        json_path = f'posts/{sub_dir}/post-{postid}.json'
        if not os.path.exists(json_path):
            # print("%d not found" % postid, end='\r')
            continue
        with open(json_path, 'r', encoding='utf-8') as f:
            post: dict = json.load(f)
        userId = post['userId']
        if userId not in map_userId_to_postid:
            map_userId_to_postid[userId] = []
        map_userId_to_postid[userId].append(postid)
    with open('map_userId_to_postid.json', 'w', encoding='utf-8') as f:
        json.dump(map_userId_to_postid, f, ensure_ascii=False, separators=(',', ':'), indent=0)

def gen_post_archive(post: dict):
    post_obj = Post(post)
    markdown = f"""---
postId: {post_obj.postid}
title: {post_obj.title}
date: {post_obj.publishTime_str}
userId: {post_obj.userId}
nickName: {post_obj.nickName}
tags: {'; '.join(tag["name"] for tag in post_obj.tagList)}
likeCount: {post_obj.likeCount}
commentCount: {post_obj.commentCount}
shareCount: {post_obj.shareCount}
favCount: {post_obj.favCount}
collection: {post_obj.diaryVo['collection']['title'] if post_obj.diaryVo and post_obj.diaryVo['collection'] is not None else ''}
collection_description: {post_obj.diaryVo['collection']['description'] if post_obj.diaryVo and post_obj.diaryVo['collection'] is not None else ''}
---

"""
    # if len(post_obj.blocks) == 1:
    #     if post_obj.blocks[0]['type'] == 3:
    #         markdown += post_obj.blocks[0]['content']
    for gameInfo in post_obj.gameInfoVo:
        gameName: str = gameInfo['gameName']
        gameStatus: int = gameInfo['gameStatus']
        lables: list[str] = [label['labelName'] for label in gameInfo['labelList']]
        status: int = gameInfo['status']
        recommendScore: float = gameInfo['recommendScore']
        markdown += f"\n```game\ngameName: {gameName}\ngameStatus: {gameStatus}\ngameLables: {'; '.join(lables)}\nstatus: {status}\nrecommendScore: {recommendScore}\n```\n\n"
    if post_obj.postType == 7:
        pass
    for block in post_obj.blocks:
        block_type = block["type"]
        if block_type == 3: # 一般文字
            markdown += block["content"]
        elif block_type == 1: # 图片
            image_url = block["image"]["url"]
            image_basename = image_url.split('/')[-1]
            local_image_src = f"./{image_basename}"
            markdown += f"\n![]({local_image_src})  \n"
        elif block_type == 6: # 评测点
            markdown += f"\n### {block['majorPost']['name']} - {block['majorPost']['score']}分 \n"
        elif block_type == 2: # 视频
            video = block["video"]
            video_url = video["url"]
            video_cover = video["coverUrl"]
            video_basename = video_url.split('/')[-1]
            local_video_src = f"./{video_basename}"
            markdown += f"\n![]({local_video_src})  \n"
        elif block_type == 4: # 投票
            vote = block["vote"]
            rich.print(vote)
            raise
            voteTitle: str = vote["voteTitle"]
            optionList: list = vote["optionList"]
        else:
            print(block)
            raise Exception("Unknown block type")
    if post_obj.hotCommentList:
        markdown += "\n\n```hotCommentList\n"
        rich.print(post_obj.hotCommentList)
        for comment in post_obj.hotCommentList:
            markdown += f"- {comment['nickName']} -reply-> {comment['toUserNickName']}:\n"
            markdown += f"> {comment['content']}\n"
        markdown += "```\n"
        print(markdown)

    # return

    post_archive_dir = f"user_archive/user-{post_obj.userId}/post-{post_obj.postid}"
    os.makedirs(post_archive_dir, exist_ok=True)
    
    shutil.copy(f"posts/{post_obj.postid//1000}/post-{post_obj.postid}.json", f"{post_archive_dir}/post-{post_obj.postid}.json")
    
    markdown_path = f"{post_archive_dir}/post-{post_obj.postid}.md"
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    donwloaded_media_dir = f"posts_media/{post_obj.postid//1000}/post-{post_obj.postid}/"
    if os.path.exists(donwloaded_media_dir):
        shutil.copytree(donwloaded_media_dir, f"{post_archive_dir}")
        print(f"copy {donwloaded_media_dir} to {post_archive_dir}")
    

if __name__ == "__main__":
    # map_users_posts()
    main()