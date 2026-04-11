import praw
import os
from dotenv import load_dotenv
import config
import json
import time
from datetime import datetime, timezone
from datetime import datetime




def in_last_six_months(time_utc):
    six_months_ago = time.time() - (180 * 24 * 60 * 60) # 180 päeva tagasi sekundites
    return time_utc >= six_months_ago


def getComments(post):
    time.sleep(0.5) #väike paus et mitte liiga kiiresti pärida, et Reddit ei keelaks
    post.comments.replace_more(limit=0)
    comments = []
    #comments_sorted = sorted(post.comments.list(), key=lambda c: c.score, reverse=True) #sordi kommentaarid skoori järgi
    for comment in post.comments.list():  # võta kogu thread
        comments.append({
            "id": comment.id,
            "body": comment.body,
            "score": comment.score,
            "depth": comment.depth,
            "created_utc": comment.created_utc,
            "author": str(comment.author) if comment.author else None,
            "parent_id": comment.parent_id,
        })

    return comments

def mentions_keyword(title, selftext, keyword):
    text = f"{title} {selftext}".lower()
    return keyword.lower() in text


def getPostsFromMultiple(reddit, subs, filter_keyword=None):
    all_posts = []
    seen_ids = set()

    for sub in subs:
        posts = getPosts(reddit, sub, filter_keyword)

        for p in posts:
            if p["id"] not in seen_ids:
                all_posts.append(p)
                seen_ids.add(p["id"])

    return all_posts



def getPosts(reddit, sub, filter_keyword=None):
    raw_count = 0

    posts = []

    # Kui keyword olemas → kasuta search()
    if filter_keyword:
        post_iterator = reddit.subreddit(sub).search(
            filter_keyword,
            sort = "new",
            #time_filter=config.TIME,
            limit=config.DEFAULT_LIMIT
        )
    else:
        post_iterator = reddit.subreddit(sub).new(
            #time_filter=config.TIME,
            limit=config.DEFAULT_LIMIT
        )




    for post in post_iterator:
        if not in_last_six_months(post.created_utc):
            break
        
        raw_count += 1
        title = post.title or ""
        selftext = post.selftext or ""

        #if not post.is_self:
        #    continue
        #if len(full_text) < config.MIN_TEXT_LENGTH:
        #    continue
        if filter_keyword and not mentions_keyword(title, selftext, filter_keyword):
            continue

        posts.append({
            "id": post.id,
            "subreddit_name": post.subreddit.display_name,
            "title": title,
            "selftext": selftext,
            "created_utc": post.created_utc,
            "score": post.score,
            "upvote_ratio": post.upvote_ratio,
            "url": post.url,
            "permalink": post.permalink,
            "comments":getComments(post)
        })
    
    print(raw_count, sub)
    return posts

def save_json(data, filepath):
    """
    Salvestab andmed JSON faili.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    
def main():
    load_dotenv()
    reddit = praw.Reddit(
        client_id = os.getenv("REDDIT_CLIENT_ID"),
        client_secret = os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent = os.getenv("REDDIT_USER_AGENT") 
    )

    os.makedirs("data/raw", exist_ok=True) #et on ok kui juba eksiteerib, makedirs teeb parentfolderid ka et koik mis puud raw folderini

    # Madala signaalitasemega alamfoorumi 
    low_data = getPostsFromMultiple(
        reddit,
        config.SUBREDDITS_LOW, #"all", #config.SUBREDDITS_LOW,
        filter_keyword=config.SUBREDDIT_HIGH
    )
    save_json(low_data, "data/raw/low.json")


    #HIGH subreddit
    high_data = getPosts(
        reddit,
        config.SUBREDDIT_HIGH
    )
    save_json(high_data, "data/raw/high.json")

    print("Low posts:", len(low_data))
    print("High posts:", len(high_data))


if __name__ == "__main__":
    main()


#python -m src.collect.collect_posts 

# 11 marketing
# 16 sales
# 121 crm
# 15 techsales
# 60 digitalmarketing
# 6 startups
# 20 entrepreneur
# 32 b2bmarketing
# 998 hubspot
# Low posts: 281
# High posts: 998