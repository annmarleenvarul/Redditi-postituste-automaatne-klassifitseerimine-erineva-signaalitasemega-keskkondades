import json
import os
import re
import emoji # pip install emoji
from langdetect import detect # pip install langdetect




def is_english(text):
    text = text.strip()
    # lühikesed agreement/sentiment tüüpi vastused jätame alles
    if re.fullmatch(r"\+1", text):
        return True

    if re.fullmatch(r"100+%+", text):
        return True
    
    try:
        return detect(text) == "en"
    except:
        return False

def clean_text(text):
    if not text:
        return ""

    text = text.replace("\n", " ").strip()

    # linkide eemaldamine
    text = re.sub(r"http\S+|www\S+", "", text)

    # liigsete tühikute eemaldamine
    text = re.sub(r"\s+", " ", text)

    # emoij eemaldamine
    text = emoji.replace_emoji(text, replace='')

    text = re.sub(r"u/\w+", "u/user", text) # user placeholder
    text = re.sub(r"r/\w+", "r/subreddit", text) # subreddit placeholder


    return text.strip()



def clean_post(post):
    title = clean_text(post.get("title", ""))
    selftext = clean_text(post.get("selftext", ""))

    # postituse tekst
    clean_post_text = f"{title} {selftext}".strip()
    comments_count_before = len(post.get("comments", []))


    # jäta välja tühjad postitused
    if not clean_post_text or clean_post_text in ["[deleted]", "[removed]"]:
        return None, comments_count_before, 0
    
    if not is_english(clean_post_text):
        return None, comments_count_before, 0
    
    cleaned_comments = []

    for c in post.get("comments", []):
        body = clean_text(c.get("body", ""))

        if not body or body in ["[deleted]", "[removed]"]:
            continue

        if not is_english(body):
            continue

        cleaned_comments.append({
            "text": body,
            "score": c.get("score", 0),
            "depth": c.get("depth", 0),
            "parent_id": c.get("parent_id"),
        })

    comments_count_after = len(cleaned_comments)

    # Thread
    thread_parts = [f"Post: {clean_post_text}"]

    for c in cleaned_comments:
        thread_parts.append(f"Comment (level {c['depth']}): {c['text']}")

    thread_text = "\n".join(thread_parts)

    cleaned_post =  {
        "id": post.get("id"),
        "subreddit_name": post.get("subreddit_name"),
        "clean_post_text": clean_post_text,
        "thread_text": thread_text,
        "comments": cleaned_comments,
        "num_comments_used": len(cleaned_comments),
        "score": post.get("score"),
        "upvote_ratio": post.get("upvote_ratio"),
        "num_comments_original": post.get("num_comments"),
        "created_utc": post.get("created_utc"),
    }
    return cleaned_post, comments_count_before, comments_count_after


# Loeme raw failis andmed, puhastame ja salvestame cleaned_data kausta
def read_write_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned = []
    total_comments_before = 0
    total_comments_after = 0

    for post in data:
        cleaned_post, len_comments_before, len_comments_after = clean_post(post)

        total_comments_before += len_comments_before
        total_comments_after += len_comments_after

        if cleaned_post:
            cleaned.append(cleaned_post)

    total_removed_comments = total_comments_before - total_comments_after

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=4)

    print(f"{input_path} -> {len(cleaned)} cleaned posts")
    print(f"Comments count before cleaning: {total_comments_before}")
    print(f"Comments count after cleaning: {total_comments_after}")
    print(f"Removed comments: {total_removed_comments}")



def main():
    os.makedirs("data/cleaned_data", exist_ok=True)

    read_write_file(
        "data/raw/low.json",
        "data/cleaned_data/low_clean.json"
    )

    read_write_file(
        "data/raw/high.json",
        "data/cleaned_data/high_clean.json"
    )


if __name__ == "__main__":
    main()

# python -m src.clean.data_cleaning

#data/raw/low.json -> 279 cleaned posts
#Comments count before cleaning: 5022
#Comments count after cleaning: 4597
#Removed comments: 425

#data/raw/high.json -> 987 cleaned posts
#Comments count before cleaning: 8550
#Comments count after cleaning: 8196
#Removed comments: 354