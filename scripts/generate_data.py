"""
Wendy's Hackathon – Local synthetic data generation.

Rewritten from 00_GCP_Setup_and_Data_Generation.ipynb for local use:
no GCP, Colab, or BigQuery. Same schemas and record counts.
Output: CSV files in data/ (or path given via --output-dir).

Usage:
    python scripts/generate_data.py
    python scripts/generate_data.py --output-dir ./data
"""

import argparse
import random
from pathlib import Path

import pandas as pd
from faker import Faker

# --- Config ---
DATA_DIR_DEFAULT = "data"
MARKET_TRENDS_ROWS = 1500
CUSTOMER_TRANSACTIONS_ROWS = 2000
CUSTOMER_FEEDBACK_ROWS = 1000
COMPETITOR_INTEL_ROWS = 1000

TREND_TEMPLATES = {
    "Gamification": [
        "Just hit a 5-day streak on the McDonald's app and got a free McFlurry. Why doesn't @Wendys have something like this? It's way more engaging.",
        "I wish the Wendy's app had weekly challenges or a spin-the-wheel game for random rewards. It would make me open it more often.",
        "Food Theory: Gamified loyalty programs are the future for fast food. Earning badges and completing missions for a free Dave's Double sounds awesome.",
    ],
    "Subscriptions": [
        "I'd totally pay $5 a month for a daily free coffee or small Frosty from Wendy's. Burger King has a coffee subscription, it's a no-brainer.",
        "Heard Panera's 'Sip Club' is a huge success. What if Wendy's did a 'Fry Club' subscription for unlimited fries? I'd sign up instantly.",
        "A monthly subscription for Wendy's that gives you free delivery and one free premium item a week would be a game-changer for my family.",
    ],
    "Personalization & Surprise": [
        "The best promos are the ones you don't expect. Got a random 'Free Frosty Friday' offer in my app today. Made my day! @Wendys",
        "My local Chick-fil-A knows I always order spicy chicken, and I get personalized offers for it. Wendy's offers feel so generic in comparison.",
        "It's my birthday month and the Starbucks app loaded a free drink for me. Does the Wendy's app do anything for birthdays? It's a missed opportunity if not.",
    ],
    "App-Exclusive Value": [
        "PRO TIP: Don't order fast food without checking the app first. The app-exclusive BOGO on the Baconator is the only way to go.",
        "It's crazy how much more expensive it is to order in-store versus using a mobile coupon. The 20% off digital orders is a huge incentive.",
        "Wendy's needs to put more of its killer deals in the app. I want a reason to use it every time, not just occasionally.",
    ],
    "Daypart Offers": [
        "I wish Wendy's had better breakfast deals. McDonald's has the 2 for $3 breakfast sandwiches which is perfect for my morning commute.",
        "That late-night 'After 8pm' deal at Taco Bell is genius. Wendy's should do a half-price Frosty or chili deal for late-night cravings.",
        "The lunch rush is real. A mobile-order-only 'Lunch Box' deal from Wendy's for like $6 would be perfect for grabbing on a short break.",
    ],
    "Tiered Loyalty": [
        "I'm a 'platinum' member at some coffee shops and get better rewards. It makes me want to go there more often than Wendy's where everyone gets the same offers.",
        "A tiered loyalty system at Wendy's would be great. The more you spend, you could unlock exclusive offers like getting to try new items early.",
    ],
}

OFFERS = ["BOGO Dave's Single", "Free Small Frosty", "20% Off Mobile Order", "4 for $4", None]
COMPETITORS = ["McDonald's", "Burger King", "Taco Bell", "Chick-fil-A"]
MECHANICS = ["BOGO", "Discount %", "Meal Deal", "Gamified App Challenge", "Loyalty Points Multiplier"]


def generate_market_trends(fake: Faker) -> pd.DataFrame:
    records = []
    themes = list(TREND_TEMPLATES.keys())
    for _ in range(MARKET_TRENDS_ROWS):
        theme = random.choice(themes)
        text_template = random.choice(TREND_TEMPLATES[theme])
        records.append({
            "source_id": fake.uuid4(),
            "source_type": random.choice(["Reddit", "FoodBlog", "X (Twitter)"]),
            "text_content": text_template,
            "publication_date": fake.date_time_this_year(),
            "trend_theme": theme,
            "velocity_score": round(random.uniform(1.0, 5.0), 2),
        })
    return pd.DataFrame(records)


def generate_customer_transactions(fake: Faker) -> pd.DataFrame:
    records = []
    for _ in range(CUSTOMER_TRANSACTIONS_ROWS):
        records.append({
            "transaction_id": fake.uuid4(),
            "customer_id": f"cust_{random.randint(100, 500)}",
            "visit_date": fake.date_time_between(start_date="-6m", end_date="now"),
            "total_spend": round(random.uniform(5.50, 25.00), 2),
            "redeemed_offer": random.choice(OFFERS),
            "channel": random.choice(["in-store", "drive-thru", "app"]),
        })
    return pd.DataFrame(records)


def generate_customer_feedback(fake: Faker) -> pd.DataFrame:
    records = []
    for _ in range(CUSTOMER_FEEDBACK_ROWS):
        records.append({
            "feedback_id": fake.uuid4(),
            "customer_id": f"cust_{random.randint(100, 500)}",
            "feedback_date": fake.date_time_between(start_date="-6m", end_date="now"),
            "rating": random.randint(1, 5),
            "feedback_text": fake.paragraph(nb_sentences=3),
        })
    return pd.DataFrame(records)


def generate_competitor_intel(fake: Faker) -> pd.DataFrame:
    records = []
    for _ in range(COMPETITOR_INTEL_ROWS):
        records.append({
            "observation_id": fake.uuid4(),
            "brand": random.choice(COMPETITORS),
            "offer_mechanic": random.choice(MECHANICS),
            "duration_days": random.randint(7, 30),
            "channel": random.choice(["app-exclusive", "all-channels", "in-store"]),
            "observed_date": fake.date_this_year(),
        })
    return pd.DataFrame(records)


def main():
    parser = argparse.ArgumentParser(description="Generate Wendy's Hackathon synthetic data (local, no GCP).")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=DATA_DIR_DEFAULT,
        help=f"Directory to write CSV files (default: {DATA_DIR_DEFAULT})",
    )
    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fake = Faker()
    print("Generating synthetic data for all agents...")

    df_market_trends = generate_market_trends(fake)
    df_market_trends.to_csv(out_dir / "market_trends.csv", index=False)
    print(f"  {len(df_market_trends)} records -> {out_dir / 'market_trends.csv'}")

    df_customer_transactions = generate_customer_transactions(fake)
    df_customer_transactions.to_csv(out_dir / "customer_transactions.csv", index=False)
    print(f"  {len(df_customer_transactions)} records -> {out_dir / 'customer_transactions.csv'}")

    df_customer_feedback = generate_customer_feedback(fake)
    df_customer_feedback.to_csv(out_dir / "customer_feedback.csv", index=False)
    print(f"  {len(df_customer_feedback)} records -> {out_dir / 'customer_feedback.csv'}")

    df_competitor_intel = generate_competitor_intel(fake)
    df_competitor_intel.to_csv(out_dir / "competitor_intel.csv", index=False)
    print(f"  {len(df_competitor_intel)} records -> {out_dir / 'competitor_intel.csv'}")

    print("Data generation complete.")


if __name__ == "__main__":
    main()
