import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

df = pd.read_csv("data/fd_users.csv")

features = [
    "age", "is_tier2_city", "sessions_before_booking",
    "avg_session_duration_min", "banks_compared",
    "preferred_tenor_months", "interest_rate_viewed",
    "days_since_last_login", "dropped_on_kyc",
    "amount_intended_inr", "is_first_time_investor",
    "support_queries_raised", "viewed_faq",
    "app_version_outdated", "time_on_rates_page_min",
    "notifications_enabled"
]

X = df[features]
y = df["churned"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

model = XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric="logloss"
)

model.fit(X_train, y_train,
          eval_set=[(X_test, y_test)],
          verbose=False)

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print("Model trained")
print(classification_report(y_test, y_pred))
print(f"ROC-AUC: {roc_auc_score(y_test, y_prob):.3f}")

joblib.dump(model, "model/churn_model.pkl")
joblib.dump(features, "model/features.pkl")
print("Model saved to model/churn_model.pkl")