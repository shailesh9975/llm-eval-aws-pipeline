# dashboard/app.py
# Reads evaluation results from DynamoDB and visualises them

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import boto3
from datetime import datetime
from decimal import Decimal

# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="LLM Eval Pipeline Dashboard",
    page_icon="☁️",
    layout="wide",
)

st.title("☁️ Cloud LLM Evaluation Pipeline")
st.caption("Live evaluation results from AWS S3 → Lambda → DynamoDB")
st.divider()

# ── DynamoDB Connection ───────────────────────────────────────────────────────

@st.cache_resource
def get_dynamodb():
    return boto3.resource("dynamodb", region_name="ap-south-1")

def load_results() -> pd.DataFrame:
    """Scan all results from DynamoDB."""
    db    = get_dynamodb()
    table = db.Table("llm-eval-results")

    response = table.scan()
    items    = response.get("Items", [])

    # Handle DynamoDB pagination
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    if not items:
        return pd.DataFrame()

    df = pd.DataFrame(items)

    # Convert Decimal to float (DynamoDB stores numbers as Decimal)
    for col in ["accuracy", "relevance", "completeness",
                "clarity", "hallucination", "final_score"]:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: float(x) if isinstance(x, Decimal) else float(x)
            )

    # Parse timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp", ascending=False)

    return df

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.markdown("**Grade Scale**")
    st.markdown("🟢 A ≥ 0.85")
    st.markdown("🔵 B ≥ 0.75")
    st.markdown("🟡 C ≥ 0.60")
    st.markdown("🔴 F < 0.60")
    st.divider()
    st.markdown("**Pipeline**")
    st.markdown("S3 → Lambda → Bedrock → DynamoDB → Dashboard")

# ── Load Data ─────────────────────────────────────────────────────────────────

with st.spinner("Loading results from DynamoDB..."):
    df = load_results()

if df.empty:
    st.warning("No evaluation results found in DynamoDB yet.")
    st.markdown("""
    **To generate results, upload a file to S3:**
```bash
    aws s3 cp your_file.json \\
      s3://llm-eval-pipeline-shailesh9975/inputs/your_file.json
```
    Then click **Refresh Data**.
    """)
    st.stop()

# ── KPI Metrics ───────────────────────────────────────────────────────────────

st.subheader("📊 Summary Metrics")

total     = len(df)
avg_score = df["final_score"].mean()
avg_acc   = df["accuracy"].mean()
avg_hall  = df["hallucination"].mean()
a_count   = (df["grade"] == "A").sum()
f_count   = (df["grade"] == "F").sum()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Evaluations", total)
c2.metric("Avg Final Score",   f"{avg_score:.3f}")
c3.metric("Avg Accuracy",      f"{avg_acc:.3f}")
c4.metric("Grade A Count",     a_count)
c5.metric("Grade F Count",     f_count,
          delta=f"-{f_count}" if f_count > 0 else None,
          delta_color="inverse")

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Trends",
    "🔬 Metric Breakdown",
    "🏆 Rankings",
    "📋 Raw Results",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Trends over time
# ══════════════════════════════════════════════════════════════════════════════

with tab1:
    st.subheader("Final Score Over Time")

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["final_score"],
        mode="lines+markers",
        name="Final Score",
        line=dict(color="#4C9BE8", width=2),
        marker=dict(size=8),
    ))
    fig1.add_hline(y=0.85, line_dash="dash",
                   line_color="green",  annotation_text="A threshold")
    fig1.add_hline(y=0.75, line_dash="dash",
                   line_color="blue",   annotation_text="B threshold")
    fig1.add_hline(y=0.60, line_dash="dash",
                   line_color="orange", annotation_text="C threshold")
    fig1.update_layout(
        yaxis=dict(title="Score", range=[0, 1]),
        xaxis=dict(title="Time"),
        height=400,
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Grade distribution pie
    st.subheader("Grade Distribution")
    grade_counts = df["grade"].value_counts().reset_index()
    grade_counts.columns = ["Grade", "Count"]

    color_map = {"A": "#2ecc71", "B": "#3498db", "C": "#f1c40f", "F": "#e74c3c"}
    fig2 = px.pie(
        grade_counts,
        names="Grade",
        values="Count",
        color="Grade",
        color_discrete_map=color_map,
        height=350,
    )
    st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Metric breakdown
# ══════════════════════════════════════════════════════════════════════════════

with tab2:
    st.subheader("Average Score Per Metric")

    metrics = ["accuracy", "relevance", "completeness", "clarity", "hallucination"]
    avgs    = [df[m].mean() for m in metrics]

    fig3 = go.Figure(go.Bar(
        x=metrics,
        y=avgs,
        marker_color=[
            "#2ecc71" if v >= 0.75 else
            "#f1c40f" if v >= 0.60 else "#e74c3c"
            for v in avgs
        ],
        text=[f"{v:.3f}" for v in avgs],
        textposition="outside",
    ))
    fig3.update_layout(
        yaxis=dict(title="Average Score", range=[0, 1]),
        height=400,
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Heatmap of all evals
    st.subheader("Metric Heatmap — All Evaluations")
    heat_df = df[metrics].round(3)
    heat_df.index = df["eval_id"].str[:8] + "..."

    fig4 = px.imshow(
        heat_df,
        color_continuous_scale="RdYlGn",
        zmin=0, zmax=1,
        aspect="auto",
        height=max(300, len(df) * 40),
    )
    st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Rankings
# ══════════════════════════════════════════════════════════════════════════════

with tab3:
    st.subheader("Top Performing Evaluations")

    top = df.nlargest(5, "final_score")[
        ["eval_id", "prompt", "final_score", "grade",
         "accuracy", "hallucination", "timestamp"]
    ].reset_index(drop=True)
    top.index += 1

    for _, row in top.iterrows():
        grade_emoji = {"A": "🟢", "B": "🔵", "C": "🟡", "F": "🔴"}.get(row["grade"], "⚪")
        with st.expander(
            f"{grade_emoji} Score: {row['final_score']} | {row['prompt'][:60]}..."
        ):
            c1, c2, c3 = st.columns(3)
            c1.metric("Final Score",  row["final_score"])
            c2.metric("Accuracy",     row["accuracy"])
            c3.metric("Hallucination",row["hallucination"])
            st.caption(f"eval_id: {row['eval_id']}")
            st.caption(f"Evaluated: {row['timestamp']}")

    st.divider()
    st.subheader("⚠️ Low Scoring Evaluations (needs review)")

    low = df[df["final_score"] < 0.60][
        ["eval_id", "prompt", "final_score", "grade", "reasoning"]
    ]

    if low.empty:
        st.success("✅ No evaluations below 0.60 threshold.")
    else:
        st.dataframe(low, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Raw results
# ══════════════════════════════════════════════════════════════════════════════

with tab4:
    st.subheader("All Evaluation Results")

    # Filter controls
    col1, col2 = st.columns(2)
    with col1:
        grade_filter = st.multiselect(
            "Filter by grade",
            options=["A", "B", "C", "F"],
            default=["A", "B", "C", "F"],
        )
    with col2:
        score_min = st.slider("Minimum score", 0.0, 1.0, 0.0, 0.05)

    filtered = df[
        (df["grade"].isin(grade_filter)) &
        (df["final_score"] >= score_min)
    ]

    st.dataframe(
        filtered[[
            "eval_id", "prompt", "final_score", "grade",
            "accuracy", "relevance", "completeness",
            "clarity", "hallucination", "reasoning", "timestamp"
        ]],
        use_container_width=True,
    )

    st.download_button(
        "⬇️ Download CSV",
        data=filtered.to_csv(index=False),
        file_name="eval_results.csv",
        mime="text/csv",
    )
