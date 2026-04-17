"""
FD Dropout Analyst — Streamlit Application
A product intelligence tool for Blostem's FD platform.
Identifies at-risk user cohorts, explains why they drop off,
and surfaces AI-generated analyst reports with recommended interventions.
"""

import json
import os
import subprocess
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import shap
import joblib
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")


# --- Page Configuration ---
st.set_page_config(
    page_title="FD Dropout Analyst | Blostem",
    page_icon="assets/favicon.png" if os.path.exists("assets/favicon.png") else None,
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- Constants ---
SCORED_DATA_PATH = "data/fd_users_scored.csv"
REPORTS_PATH = "model/analyst_reports.json"
MODEL_PATH = "model/churn_model.pkl"
FEATURES_PATH = "model/features.pkl"

COHORT_COLORS = {
    "KYC Dropout": "#E8533F",
    "Comparison Paralysis": "#F4A623",
    "Overwhelmed First-Timer": "#7B68EE",
    "Silent Churner": "#5B8DB8",
    "Unclassified": "#AAAAAA"
}

RISK_COLORS = {
    "High Risk": "#E8533F",
    "Medium Risk": "#F4A623",
    "Low Risk": "#4CAF50"
}


# --- Data Loaders ---
@st.cache_data
def load_scored_data():
    df = pd.read_csv(SCORED_DATA_PATH)
    return df


@st.cache_data
def load_reports():
    with open(REPORTS_PATH, "r") as f:
        return json.load(f)


@st.cache_resource
def load_model():
    model = joblib.load(MODEL_PATH)
    features = joblib.load(FEATURES_PATH)
    return model, features


# --- Sidebar ---
def render_sidebar():
    st.sidebar.markdown("## FD Dropout Analyst")
    st.sidebar.markdown("*Blostem AI Builder Hackathon*")
    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigation",
        ["Platform Overview", "Cohort Intelligence", "AI Analyst Reports", "User Risk Scorer"],
        label_visibility="collapsed"
    )

    st.sidebar.divider()
    st.sidebar.markdown("**Data**")
    st.sidebar.caption("3,000 synthetic FD user profiles")
    st.sidebar.caption("XGBoost · ROC-AUC 0.939")
    st.sidebar.caption("RAG · LLaMA 3.3 70B · FAISS")

    return page


# --- Page 1: Platform Overview ---
def render_overview(df):
    st.title("FD Dropout Analyst")
    st.markdown(
        "Behavioral intelligence for Blostem's FD platform — "
        "identifying which users will drop off, why, and what to do about it."
    )
    st.divider()

    high_risk = df[df["risk_tier"] == "High Risk"]
    classified = df[
        (df["cohort"] != "Unclassified") &
        (df["risk_tier"] == "High Risk")
    ]
    avg_churn = df["churn_probability"].mean()
    potential_loss = high_risk["amount_intended_inr"].sum() / 1e7

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Users", f"{len(df):,}")
    col2.metric("High Risk Users", f"{len(high_risk):,}",
                delta=f"{len(high_risk)/len(df)*100:.1f}% of platform")
    col3.metric("Avg Churn Probability", f"{avg_churn:.1%}")
    col4.metric("At-Risk Deposit Value", f"₹{potential_loss:.1f}Cr")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Risk Distribution")
        risk_counts = df["risk_tier"].value_counts().reset_index()
        risk_counts.columns = ["Risk Tier", "Users"]
        fig = px.pie(
            risk_counts,
            names="Risk Tier",
            values="Users",
            color="Risk Tier",
            color_discrete_map=RISK_COLORS,
            hole=0.45
        )
        fig.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Dropout Cohort Breakdown")
        cohort_counts = (
            classified["cohort"]
            .value_counts()
            .reset_index()
        )
        cohort_counts.columns = ["Cohort", "Users"]
        fig2 = px.bar(
            cohort_counts,
            x="Users",
            y="Cohort",
            orientation="h",
            color="Cohort",
            color_discrete_map=COHORT_COLORS,
            text="Users"
        )
        fig2.update_layout(
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            yaxis=dict(categoryorder="total ascending")
        )
        fig2.update_traces(textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("Churn Probability by City")
    city_churn = (
        df.groupby("city")["churn_probability"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    city_churn.columns = ["City", "Avg Churn Probability"]
    fig3 = px.bar(
        city_churn,
        x="City",
        y="Avg Churn Probability",
        color="Avg Churn Probability",
        color_continuous_scale="Reds",
        text=city_churn["Avg Churn Probability"].apply(lambda x: f"{x:.1%}")
    )
    fig3.update_layout(
        margin=dict(t=20, b=20),
        coloraxis_showscale=False
    )
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)


# --- Page 2: Cohort Intelligence ---
def render_cohort_intelligence(df):
    st.title("Cohort Intelligence")
    st.markdown(
        "High-risk users segmented into behavioral cohorts. "
        "Each cohort has a distinct dropout pattern and requires a different intervention."
    )
    st.divider()

    cohorts = ["KYC Dropout", "Comparison Paralysis",
               "Overwhelmed First-Timer", "Silent Churner"]
    selected = st.selectbox("Select Cohort", cohorts)

    cohort_df = df[df["cohort"] == selected].copy()
    st.markdown(f"**{len(cohort_df)} users** in this cohort")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Churn Probability",
                f"{cohort_df['churn_probability'].mean():.1%}")
    col2.metric("Avg Days Since Login",
                f"{cohort_df['days_since_last_login'].mean():.0f} days")
    col3.metric("First-Time Investors",
                f"{cohort_df['is_first_time_investor'].mean()*100:.0f}%")
    col4.metric("KYC Drop Rate",
                f"{cohort_df['dropped_on_kyc'].mean()*100:.0f}%")

    st.divider()

    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("Banks Compared Distribution")
        fig = px.histogram(
            cohort_df,
            x="banks_compared",
            nbins=6,
            color_discrete_sequence=[COHORT_COLORS.get(selected, "#888")]
        )
        fig.update_layout(
            xaxis_title="Banks Compared",
            yaxis_title="Users",
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("Sessions Before Drop-off")
        fig2 = px.histogram(
            cohort_df,
            x="sessions_before_booking",
            nbins=8,
            color_discrete_sequence=[COHORT_COLORS.get(selected, "#888")]
        )
        fig2.update_layout(
            xaxis_title="Sessions",
            yaxis_title="Users",
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("User Table")
    display_cols = [
        "user_id", "age", "city", "days_since_last_login",
        "banks_compared", "dropped_on_kyc",
        "churn_probability", "risk_tier"
    ]
    st.dataframe(
        cohort_df[display_cols]
        .sort_values("churn_probability", ascending=False)
        .head(50)
        .reset_index(drop=True),
        use_container_width=True
    )


# --- Page 3: AI Analyst Reports ---
def render_analyst_reports(reports):
    st.title("AI Analyst Reports")
    st.markdown(
        "RAG-powered reports generated from cohort behavioral data "
        "and a knowledge base of Indian fintech and FD domain context. "
        "Each report surfaces the finding, root cause, and recommended intervention."
    )
    st.divider()

    for cohort_name, data in reports.items():
        color = COHORT_COLORS.get(cohort_name, "#888")
        stats = data["cohort_stats"]
        report = data["analyst_report"]

        with st.expander(f"{cohort_name}  —  {stats['user_count']} users  "
                         f"|  Avg churn: {stats['avg_churn_probability']:.1%}",
                         expanded=True):

            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Days Inactive", stats["avg_days_since_login"])
            col2.metric("KYC Drop Rate", f"{stats['pct_dropped_kyc']}%")
            col3.metric("First-Time Investors", f"{stats['pct_first_time']}%")

            st.divider()
            st.markdown("**AI Analyst Report**")
            st.markdown(
                f"""
                <div style="
                    background-color: #1a1a2e;
                    border-left: 4px solid {color};
                    padding: 20px 24px;
                    border-radius: 6px;
                    font-size: 0.95rem;
                    line-height: 1.7;
                    color: #e0e0e0;
                    white-space: pre-wrap;
                ">
{report}
                </div>
                """,
                unsafe_allow_html=True
            )


# --- Page 4: User Risk Scorer ---
def render_user_scorer(model, features):
    st.title("User Risk Scorer")
    st.markdown(
        "Score an individual user's churn probability in real time. "
        "Enter their behavioral signals to get a risk assessment."
    )
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.slider("Age", 18, 65, 30)
        sessions = st.slider("Sessions before booking", 1, 18, 5)
        duration = st.slider("Avg session duration (min)", 1.0, 22.0, 7.0)
        banks = st.slider("Banks compared", 1, 7, 2)
        is_tier2 = st.selectbox("Tier 2 city?", [0, 1],
                                format_func=lambda x: "Yes" if x else "No")

    with col2:
        tenor = st.selectbox("Preferred tenor (months)", [3, 6, 12, 24, 36])
        rate = st.slider("Interest rate viewed (%)", 6.5, 9.5, 8.0)
        days_login = st.slider("Days since last login", 0, 65, 15)
        kyc_drop = st.selectbox("Dropped on KYC?", [0, 1],
                                format_func=lambda x: "Yes" if x else "No")
        amount = st.selectbox(
            "Amount intended (Rs)",
            [10000, 25000, 50000, 100000, 200000, 500000],
            index=2
        )

    with col3:
        first_time = st.selectbox("First-time investor?", [0, 1],
                                  format_func=lambda x: "Yes" if x else "No")
        support = st.slider("Support queries raised", 0, 5, 0)
        faq = st.selectbox("Viewed FAQ?", [0, 1],
                           format_func=lambda x: "Yes" if x else "No")
        outdated = st.selectbox("Outdated app version?", [0, 1],
                                format_func=lambda x: "Yes" if x else "No")
        time_rates = st.slider("Time on rates page (min)", 0.5, 15.0, 3.0)
        notifs = st.selectbox("Notifications enabled?", [0, 1],
                              format_func=lambda x: "Yes" if x else "No")

    st.divider()

    if st.button("Score This User", type="primary", use_container_width=True):
        input_data = pd.DataFrame([[
            age, is_tier2, sessions, duration, banks, tenor,
            rate, days_login, kyc_drop, amount,
            first_time, support, faq, outdated, time_rates, notifs
        ]], columns=features)

        prob = model.predict_proba(input_data)[0][1]

        col_result, col_shap = st.columns([1, 2])

        with col_result:
            if prob > 0.7:
                st.error(f"High Risk\n\n**{prob:.1%}** churn probability")
                st.markdown("Trigger immediate intervention.")
            elif prob > 0.4:
                st.warning(f"Medium Risk\n\n**{prob:.1%}** churn probability")
                st.markdown("Monitor and nudge within 48 hours.")
            else:
                st.success(f"Low Risk\n\n**{prob:.1%}** churn probability")
                st.markdown("No immediate action required.")

        with col_shap:
            st.markdown("**Feature Contributions (SHAP)**")
            explainer = shap.TreeExplainer(model)
            shap_vals = explainer.shap_values(input_data)
            fig, ax = plt.subplots(figsize=(6, 3))
            shap.waterfall_plot(
                shap.Explanation(
                    values=shap_vals[0],
                    base_values=explainer.expected_value,
                    data=input_data.iloc[0],
                    feature_names=features
                ),
                show=False,
                max_display=8
            )
            st.pyplot(fig, use_container_width=True)
            plt.close()


# --- Main ---
def main():
    # Run segmentation pipeline on startup if scored data is stale
    if not os.path.exists(SCORED_DATA_PATH):
        with st.spinner("Running segmentation pipeline..."):
            subprocess.run([sys.executable, "model/segment.py"], check=True)

    df = load_scored_data()
    reports = load_reports()
    model, features = load_model()

    page = render_sidebar()

    if page == "Platform Overview":
        render_overview(df)
    elif page == "Cohort Intelligence":
        render_cohort_intelligence(df)
    elif page == "AI Analyst Reports":
        render_analyst_reports(reports)
    elif page == "User Risk Scorer":
        render_user_scorer(model, features)


if __name__ == "__main__":
    main()