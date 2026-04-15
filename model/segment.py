import pandas as pd
import numpy as np
import joblib
import json
import os


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def load_data_and_model():
    df = pd.read_csv("data/fd_users.csv")
    model = joblib.load("model/churn_model.pkl")
    features = joblib.load("model/features.pkl")
    return df, model, features


def score_users(df, model, features):
    X = df[features]
    df["churn_probability"] = model.predict_proba(X)[:, 1]
    df["risk_tier"] = pd.cut(
        df["churn_probability"],
        bins=[0, 0.4, 0.7, 1.0],
        labels=["Low Risk", "Medium Risk", "High Risk"]
    )
    return df


def assign_cohort(df):
    df["cohort"] = "Unclassified"

    mask_kyc = (
        (df["dropped_on_kyc"] == 1) &
        (df["support_queries_raised"] >= 2) &
        (df["churn_probability"] > 0.5)
    )
    df.loc[mask_kyc, "cohort"] = "KYC Dropout"

    mask_cp = (
        (df["banks_compared"] >= 4) &
        (df["sessions_before_booking"] >= 8) &
        (df["days_since_last_login"] > 15) &
        (df["churn_probability"] > 0.5)
    )
    df.loc[mask_cp & (df["cohort"] == "Unclassified"), "cohort"] = "Comparison Paralysis"

    mask_ft = (
        (df["is_first_time_investor"] == 1) &
        (df["viewed_faq"] == 0) &
        (df["sessions_before_booking"] >= 6) &
        (df["churn_probability"] > 0.5)
    )
    df.loc[mask_ft & (df["cohort"] == "Unclassified"), "cohort"] = "Overwhelmed First-Timer"

    mask_silent = (
        (df["days_since_last_login"] > 30) &
        (df["avg_session_duration_min"] < 4) &
        (df["churn_probability"] > 0.5)
    )
    df.loc[mask_silent & (df["cohort"] == "Unclassified"), "cohort"] = "Silent Churner"

    return df


def compute_cohort_stats(df):
    high_risk = df[df["churn_probability"] > 0.5].copy()
    cohorts = high_risk[high_risk["cohort"] != "Unclassified"]["cohort"].unique()

    cohort_stats = {}

    for cohort in cohorts:
        group = high_risk[high_risk["cohort"] == cohort]

        stats = {
            "cohort_name": cohort,
            "user_count": len(group),
            "avg_churn_probability": round(float(group["churn_probability"].mean()), 3),
            "avg_age": round(float(group["age"].mean()), 1),
            "pct_tier2_city": round(float(group["is_tier2_city"].mean() * 100), 1),
            "avg_days_since_login": round(float(group["days_since_last_login"].mean()), 1),
            "avg_banks_compared": round(float(group["banks_compared"].mean()), 1),
            "avg_sessions": round(float(group["sessions_before_booking"].mean()), 1),
            "pct_dropped_kyc": round(float(group["dropped_on_kyc"].mean() * 100), 1),
            "pct_first_time": round(float(group["is_first_time_investor"].mean() * 100), 1),
            "avg_support_queries": round(float(group["support_queries_raised"].mean()), 2),
            "pct_viewed_faq": round(float(group["viewed_faq"].mean() * 100), 1),
            "avg_amount_intended": round(float(group["amount_intended_inr"].mean()), 0),
            "top_city": str(group["city"].mode()[0]) if len(group) > 0 else "N/A",
            "avg_interest_rate_viewed": round(float(group["interest_rate_viewed"].mean()), 2),
        }
        cohort_stats[cohort] = stats

    return cohort_stats


def run_segmentation():
    print("🔄 Loading data and model...")
    df, model, features = load_data_and_model()

    print("📊 Scoring users...")
    df = score_users(df, model, features)

    print("🗂️ Assigning cohorts...")
    df = assign_cohort(df)

    print("📈 Computing cohort stats...")
    cohort_stats = compute_cohort_stats(df)

    df.to_csv("data/fd_users_scored.csv", index=False)
    print("✅ Scored dataset saved to data/fd_users_scored.csv")

    os.makedirs("model", exist_ok=True)
    with open("model/cohort_stats.json", "w") as f:
        json.dump(cohort_stats, f, indent=2, cls=NumpyEncoder)
    print("✅ Cohort stats saved to model/cohort_stats.json")

    print("\n📋 COHORT SUMMARY:")
    print("-" * 50)
    for name, stats in cohort_stats.items():
        print(f"\n🔴 {name}")
        print(f"   Users: {stats['user_count']}")
        print(f"   Avg Churn Probability: {stats['avg_churn_probability']}")
        print(f"   Avg Days Since Login: {stats['avg_days_since_login']}")
        print(f"   % Dropped on KYC: {stats['pct_dropped_kyc']}%")
        print(f"   % First-Time Investor: {stats['pct_first_time']}%")
        print(f"   Top City: {stats['top_city']}")

    return df, cohort_stats


if __name__ == "__main__":
    df, cohort_stats = run_segmentation()