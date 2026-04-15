import pandas as pd
import numpy as np

np.random.seed(42)
n = 3000

banks = ["Suryoday SFB", "ESAF SFB", "Ujjivan SFB", "AU SFB", "Jana SFB", "Equitas SFB"]
tenors = [3, 6, 12, 24, 36]
cities_tier1 = ["Mumbai", "Delhi", "Bengaluru", "Pune", "Chennai"]
cities_tier2 = ["Gorakhpur", "Patna", "Lucknow", "Bhopal", "Surat", "Jaipur", "Coimbatore", "Nagpur"]
cities = cities_tier1 * 3 + cities_tier2 * 5  # weighted toward Tier 2

df = pd.DataFrame({
    "user_id": [f"USR{str(i).zfill(4)}" for i in range(1, n+1)],
    "age": np.random.randint(22, 62, n),
    "city": np.random.choice(cities, n),
    "is_tier2_city": [1 if c in cities_tier2 else 0 for c in np.random.choice(cities, n)],
    "sessions_before_booking": np.random.randint(1, 18, n),
    "avg_session_duration_min": np.round(np.random.uniform(1.0, 22.0, n), 2),
    "banks_compared": np.random.randint(1, 7, n),
    "preferred_tenor_months": np.random.choice(tenors, n),
    "interest_rate_viewed": np.round(np.random.uniform(6.5, 9.5, n), 2),
    "days_since_last_login": np.random.randint(0, 65, n),
    "dropped_on_kyc": np.random.choice([0, 1], n, p=[0.65, 0.35]),
    "amount_intended_inr": np.random.choice([10000, 25000, 50000, 100000, 200000, 500000], n),
    "is_first_time_investor": np.random.choice([0, 1], n, p=[0.35, 0.65]),
    "support_queries_raised": np.random.randint(0, 6, n),
    "viewed_faq": np.random.choice([0, 1], n, p=[0.4, 0.6]),
    "app_version_outdated": np.random.choice([0, 1], n, p=[0.75, 0.25]),
    "time_on_rates_page_min": np.round(np.random.uniform(0.5, 15.0, n), 2),
    "notifications_enabled": np.random.choice([0, 1], n, p=[0.3, 0.7]),
})

# Realistic churn logic with multiple dropout personas
kyc_dropout = (df["dropped_on_kyc"] == 1) & (df["support_queries_raised"] >= 2)
comparison_paralysis = (df["banks_compared"] >= 5) & (df["sessions_before_booking"] >= 10) & (df["days_since_last_login"] > 20)
inactive_browser = (df["days_since_last_login"] > 35) & (df["avg_session_duration_min"] < 4)
overwhelmed_firsttimer = (df["is_first_time_investor"] == 1) & (df["viewed_faq"] == 0) & (df["sessions_before_booking"] >= 8)

df["dropout_reason"] = "retained"
df.loc[inactive_browser, "dropout_reason"] = "inactive_browser"
df.loc[overwhelmed_firsttimer, "dropout_reason"] = "overwhelmed_firsttimer"
df.loc[comparison_paralysis, "dropout_reason"] = "comparison_paralysis"
df.loc[kyc_dropout, "dropout_reason"] = "kyc_dropout"  # highest priority

df["churned"] = (df["dropout_reason"] != "retained").astype(int)
# Add 5% noise to make model realistic
noise_idx = df.sample(frac=0.05, random_state=7).index
df.loc[noise_idx, "churned"] = 1 - df.loc[noise_idx, "churned"]

df.to_csv("data/fd_users.csv", index=False)
print(f"Dataset saved: {df.shape}")
print(df["dropout_reason"].value_counts())