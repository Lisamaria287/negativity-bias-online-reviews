"""
yelp_sample.py
--------------
Turns the (huge) Yelp Open Dataset into two small CSV files you can open
in jamovi, JASP, SPSS or Excel.

What it does:
  1. Reads the business file and finds all restaurants.
  2. Reads the review file line by line (so it never runs out of memory).
  3. Keeps a random sample of restaurant reviews (default: 50,000).
  4. Adds useful extra columns: word count, review age, star group, etc.
  5. Writes:
       reviews_sample.csv            -> for your statistics (no review text)
       reviews_sample_with_text.csv  -> same rows + the review text (for reading
                                        examples and any later text analysis)

How to run it (see the project plan for screenshots-in-words):
  1. Put this file in the same folder as
       yelp_academic_dataset_business.json
       yelp_academic_dataset_review.json
  2. Open a terminal / command prompt in that folder and type:
       python yelp_sample.py
     (on a Mac you may need: python3 yelp_sample.py)

Optional settings:
       python yelp_sample.py --n 20000 --seed 7
  --n     how many reviews to sample (default 50000)
  --seed  random seed; keep it the same so your sample is reproducible

Only uses Python's built-in libraries, so nothing needs to be installed.
"""

import argparse
import csv
import json
import math
import random
from datetime import date

BUSINESS_FILE = "yelp_academic_dataset_business.json"
REVIEW_FILE = "yelp_academic_dataset_review.json"
OUT_STATS = "reviews_sample.csv"
OUT_TEXT = "reviews_sample_with_text.csv"


def parse_day(date_string):
    """Yelp dates look like '2018-07-07 22:09:11'. Keep only the day."""
    return date.fromisoformat(date_string[:10])


def star_group(stars):
    if stars <= 2:
        return "negative"
    if stars == 3:
        return "neutral"
    return "positive"


def load_restaurants():
    """Return {business_id: (city, state)} for every business tagged 'Restaurants'."""
    restaurants = {}
    with open(BUSINESS_FILE, encoding="utf-8") as f:
        for line in f:
            b = json.loads(line)
            categories = b.get("categories") or ""
            tags = [c.strip() for c in categories.split(",")]
            if "Restaurants" in tags:
                restaurants[b["business_id"]] = (b.get("city", ""), b.get("state", ""))
    return restaurants


def sample_reviews(restaurants, n, seed):
    """
    Reservoir sampling: walks through every restaurant review once and keeps a
    truly random sample of n, without loading the whole file into memory.
    Also tracks the most recent review date (needed to compute review age).
    """
    rng = random.Random(seed)
    sample = []
    seen = 0
    latest_day = None

    with open(REVIEW_FILE, encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            r = json.loads(line)
            day = parse_day(r["date"])
            if latest_day is None or day > latest_day:
                latest_day = day

            if r["business_id"] not in restaurants:
                continue

            seen += 1
            if len(sample) < n:
                sample.append(r)
            else:
                j = rng.randrange(seen)
                if j < n:
                    sample[j] = r

            if line_number % 1_000_000 == 0:
                print(f"  ...read {line_number:,} reviews so far")

    return sample, seen, latest_day


def main():
    parser = argparse.ArgumentParser(description="Sample Yelp restaurant reviews to CSV.")
    parser.add_argument("--n", type=int, default=50_000, help="number of reviews to sample")
    parser.add_argument("--seed", type=int, default=42, help="random seed (for reproducibility)")
    args = parser.parse_args()

    print("Step 1/3: finding restaurants in the business file...")
    restaurants = load_restaurants()
    print(f"  found {len(restaurants):,} restaurants")

    print("Step 2/3: sampling reviews (this can take 5-20 minutes)...")
    sample, seen, latest_day = sample_reviews(restaurants, args.n, args.seed)
    print(f"  restaurant reviews in the full dataset: {seen:,}")
    print(f"  kept a random sample of {len(sample):,}")
    print(f"  most recent review date in the dataset: {latest_day}")

    print("Step 3/3: writing CSV files...")
    stats_columns = [
        "review_id", "business_id", "city", "state",
        "stars", "star_group", "useful", "log_useful", "funny", "cool",
        "date", "year", "review_age_days",
        "word_count", "exclamation_marks",
    ]
    with open(OUT_STATS, "w", newline="", encoding="utf-8") as f_stats, \
         open(OUT_TEXT, "w", newline="", encoding="utf-8") as f_text:
        w_stats = csv.DictWriter(f_stats, fieldnames=stats_columns)
        w_text = csv.DictWriter(f_text, fieldnames=stats_columns + ["text"])
        w_stats.writeheader()
        w_text.writeheader()

        for r in sample:
            day = parse_day(r["date"])
            text = r.get("text", "")
            city, state = restaurants[r["business_id"]]
            stars = int(round(float(r["stars"])))
            useful = int(r.get("useful", 0))
            row = {
                "review_id": r["review_id"],
                "business_id": r["business_id"],
                "city": city,
                "state": state,
                "stars": stars,
                "star_group": star_group(stars),
                "useful": useful,
                "log_useful": round(math.log(useful + 1), 4),
                "funny": int(r.get("funny", 0)),
                "cool": int(r.get("cool", 0)),
                "date": day.isoformat(),
                "year": day.year,
                "review_age_days": (latest_day - day).days,
                "word_count": len(text.split()),
                "exclamation_marks": text.count("!"),
            }
            w_stats.writerow(row)
            w_text.writerow({**row, "text": text})

    print(f"Done! Created {OUT_STATS} and {OUT_TEXT}")


if __name__ == "__main__":
    main()
