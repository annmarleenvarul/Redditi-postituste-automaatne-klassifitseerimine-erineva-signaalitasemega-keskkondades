import json
import os
from src.clean.data_cleaning import clean_text, is_english


def clean_post_for_llm(post):
    clean_title = clean_text(post.get("title", ""))
    clean_selftext = clean_text(post.get("selftext", ""))

    clean_post_text = f"{clean_title} {clean_selftext}".strip()

    # jäta välja tühjad postitused
    if not clean_post_text or clean_post_text in ["[deleted]", "[removed]"]:
        return None
    
    if not is_english(clean_post_text):
        return None

    cleaned_comments = []

    for c in post.get("comments", []):
        body = clean_text(c.get("body", ""))

        if not body or body in ["[deleted]", "[removed]"]:
            continue
        if not is_english(body):
            continue

        cleaned_comments.append({
            "id": c.get("id"),                     
            "text": body,
            "score": c.get("score", 0),
            "depth": c.get("depth", 0),
            "parent_id": c.get("parent_id"),
        })

    cleaned_for_llm = {
        "id": post.get("id"),
        "subreddit_name": post.get("subreddit_name"),
        "clean_title" : clean_text(post.get("title", "")),
        "clean_selftext" : clean_text(post.get("selftext", "")),
        "comments": cleaned_comments,
        "num_of_comments": len(cleaned_comments),
        "score": post.get("score"),
        "upvote_ratio": post.get("upvote_ratio"),
        "created_utc": post.get("created_utc"),
    }

    cleaned_for_llm["thread_for_llm"] = format_thread_for_llm(cleaned_for_llm)

    return cleaned_for_llm


def parent_id_format(parent_id, post_id):
    # t3 - kommetnaar vastab postitusele
    # t1 - kommentaar vastab teisele kommentaarile

    if not parent_id:
        return f"post_{post_id}"

    if parent_id.startswith("t3_"):
        return f"post_{post_id}"

    if parent_id.startswith("t1_"):
        return f"comment_{parent_id[3:]}"

    return parent_id


def format_thread_for_llm(post):
    post_id = post["id"]
    subreddit = post["subreddit_name"]
    comments = post["comments"]

    lines = []
    lines.append(f"SUBREDDIT: {subreddit}")
    lines.append("")
    lines.append(f"POST [post_id_{post_id}]")
    lines.append(f"TITLE: {post['clean_title']}")
    lines.append(f"BODY: {post['clean_selftext']}")
    lines.append("")
    lines.append("COMMENTS:")
    lines.append("")

    for c in comments:
        comment_id = c.get("id") or "unknown"
        depth = c.get("depth", 0)
        parent = parent_id_format(c.get("parent_id"), post_id)
        score = c.get("score", 0)
        text = c.get("text", "").strip()

        indent = "  " * depth

        lines.append(f"{indent}COMMENT [comment_id_{comment_id}]")
        lines.append(f"{indent}parent_id: {parent}")
        lines.append(f"{indent}depth: {depth}")
        lines.append(f"{indent}score: {score}")
        lines.append(f"{indent}text: {text}")
        lines.append("")
    
    thread = "\n".join(lines).strip()

    return thread



# Loeme raw failis andmed, puhastame ja salvestame cleaned_data kausta
def read_write_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    clean_for_llm = []
    for post in data:
        cleaned = clean_post_for_llm(post)
        if cleaned:
            clean_for_llm.append(cleaned)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(clean_for_llm, f, ensure_ascii=False, indent=4)

    print(f"{output_path} -> {len(clean_for_llm)} cleaned posts")



def main():
    os.makedirs("data/llm_formatted", exist_ok=True)
    read_write_file("data/raw/low.json", "data/llm_formatted/low_llm.json" )
    read_write_file( "data/raw/high.json", "data/llm_formatted/high_llm.json")


if __name__ == "__main__":
    main()


#python -m src.clean.clean_format_llm 