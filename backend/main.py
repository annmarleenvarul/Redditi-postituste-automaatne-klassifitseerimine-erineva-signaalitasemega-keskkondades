from datetime import datetime
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from typing import Optional
from collections import Counter
import math

app = FastAPI()

app.add_middleware( CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], )

# MVP kasutab eelnevalt kogutud, puhastatud ja analüüsitud andmeid 
DATA_PATH = "../data/thread_level_results/thread_results_mvp.json"

def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def format_date(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%d.%m.%Y")

@app.get("/api/threads")
def get_threads(
    # algsed filtrid
    sentiment: Optional[str] = Query(None), # meelestatuse filter
    product_feedback: Optional[bool] = Query(None), # toote tagasiside filter
    subreddit: Optional[str] = Query(None), # alamfoorumi filter
    labels: Optional[str] = Query(None), # lisa filtrid
    page: int = Query(1), # lehekülje number
    page_size: int = Query(10), # mitu lõime korraga näidatakse
):
    data = load_data()
    threads = data if isinstance(data, list) else list(data.values())

    # meelestatuse filter
    if sentiment:
        sentiment_list = [s.strip() for s in sentiment.split(',')]
        threads = [t for t in threads if t.get("llm_sentiment") in sentiment_list]

    # toote tagasiside filter
    if product_feedback is not None:
        threads = [t for t in threads if bool(t.get("product_feedback")) == product_feedback]

    # lisa filtrid
    if labels:
        label_list = [l.strip() for l in labels.split(',') if l.strip()]
        threads = [t for t in threads if all(l in (t.get('labels') or []) + (t.get('additional_labels') or []) for l in label_list)]

    # alamfoorumi filter
    if subreddit:
        threads = [t for t in threads if t.get("raw_subreddit_name", "").lower() == subreddit.lower()]

    total = len(threads)

    threads = sorted(threads, key=lambda t: t.get("relevancy_score", 0) or 0, reverse=True)

    # mis lõimi juurde anda kasutajaliidesele
    start = (page - 1) * page_size
    page_threads = threads[start:start+page_size]

    result = []
    for t in page_threads:
        comments = t.get("raw_comments") or []
        num_comments = len(comments)
        ts = t.get("raw_created_utc") or 0
        labels = t.get("labels") or []
        if t.get("additional_labels"):
            labels = labels + t["additional_labels"]
        labels = list(dict.fromkeys(labels))  # deduplicate

        highlights = t.get("highlights_for_mvp") or t.get("highlights") or []

        result.append({
            "id": t.get("id"),
            "subreddit": t.get("raw_subreddit_name", ""),
            "title": t.get("raw_title", ""),
            "sentiment": t.get("llm_sentiment", "neutral"),
            "product_feedback": bool(t.get("product_feedback")),
            "labels": labels,
            "summary_et": t.get("summary_et", ""),
            "score": t.get("raw_score", 0),
            "num_comments": num_comments,
            "created": format_date(ts) if ts else "",
            "url": t.get("raw_url", ""),
            "relevancy_score": t.get("relevancy_score", 0),
            "highlights": highlights,
        })

    return {
        "threads": result,
        "total": total,
        "page": page,
        "pages": math.ceil(total / page_size),
    }




@app.get("/api/stats")
def get_stats(subreddit: Optional[str] = Query(None)):
    data = load_data()
    threads = data if isinstance(data, list) else list(data.values())

    # kui valitud konkreetne subreddit
    if subreddit:
        threads = [t for t in threads if t.get("raw_subreddit_name", "").lower() == subreddit.lower()]

    total = len(threads)
    sentiments = Counter(t.get("llm_sentiment", "neutral") for t in threads)
    product_feedback_count = sum(1 for t in threads if t.get("product_feedback"))

    neg_percent = round(sentiments.get("negative", 0) / total * 100) if total else 0
    pos_percent = round(sentiments.get("positive", 0) / total * 100) if total else 0
    neu_percent = round(sentiments.get("neutral", 0) / total * 100) if total else 0
    fb_percent = round(product_feedback_count / total * 100) if total else 0

    sub_counts = Counter(t.get("raw_subreddit_name", "") for t in threads)
    subreddits = [
        {"name": name, "count": count, "pct": round(count / total * 100) if total else 0}
        for name, count in sub_counts.most_common(8)
    ]

    return {
        "total": total,
        "negative_pct": neg_percent,
        "positive_pct": pos_percent,
        "neutral_pct": neu_percent,
        "product_feedback_pct": fb_percent,
        "subreddits": subreddits,
        "sentiment_distribution": {
            "negative": neg_percent,
            "positive": pos_percent,
            "neutral": neu_percent,
        }
    }

@app.get("/api/thread/{thread_id}")
def get_thread_detail(thread_id: str):
    import re

    # normaliseerime teksti, et highlighte leida
    def normalize(text):
        if not text:
            return ""
        return re.sub(r"\s+", " ", str(text)).strip()

    def contains_highlight(text, quotes):
        n = normalize(text).lower()
        for q in quotes:
            if not q:
                continue
            if normalize(q).lower() in n:
                return True
            # leiame, algse osa mis on sama
            partial = normalize(q).lower()[:40]
            if len(partial) >= 15 and partial in n:
                return True
        return False

    data = load_data()
    threads = data if isinstance(data, list) else list(data.values())
    for t in threads:
        if str(t.get("id")) == thread_id:
            highlights = t.get("highlights_for_mvp") or t.get("highlights") or []
            highlight_quotes = [h.get("quote", "") for h in highlights if h.get("quote")]

            all_comments = t.get("raw_comments") or []

            by_id = {c["id"]: c for c in all_comments}

            matching_ids = set()
            for c in all_comments:
                if contains_highlight(c.get("body", ""), highlight_quotes):
                    matching_ids.add(c["id"])
                    cur = c
                    while True:
                        pid = cur.get("parent_id", "")
                        if pid.startswith("t1_"):
                            parent_id = pid[3:]
                            if parent_id in by_id:
                                matching_ids.add(parent_id)
                                cur = by_id[parent_id]
                            else:
                                break
                        else:
                            break

            filtered = [c for c in all_comments if c["id"] in matching_ids]
            filtered.sort(key=lambda c: c.get("depth", 0))

            selftext = t.get("raw_selftext") or ""
            show_selftext = contains_highlight(selftext, highlight_quotes) or bool(matching_ids)

            return {
                "id": t.get("id"),
                "title": t.get("raw_title", ""),
                "url": t.get("raw_url", ""),
                "selftext": selftext if show_selftext else "",
                "comments": filtered,
                "highlights": highlights,
                "highlight_quotes": highlight_quotes,
            }
    return {"error": "not found"}