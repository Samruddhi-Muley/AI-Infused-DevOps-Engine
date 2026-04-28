import streamlit as st
import sqlite3
import pandas as pd
from memory.db import DB_PATH

st.set_page_config(page_title="AIDE Dashboard", page_icon="📊", layout="wide")
st.title("📊 AIDE Analytics Dashboard")

try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM fix_history", conn)
    conn.close()
except Exception as e:
    st.error(f"Could not load history: {e}")
    st.stop()

if df.empty:
    st.info("No fix history yet. Run AIDE on some logs first!")
    st.stop()

# ── Key Metrics ──────────────────────────────────────────────────────
total     = len(df)
succeeded = int(df["success"].sum())
failed    = total - succeeded
rate      = (succeeded / total * 100) if total > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Attempts",  total)
col2.metric("Successful",      f"{succeeded} ✅")
col3.metric("Failed",          f"{failed} ❌")
col4.metric("Success Rate",    f"{rate:.1f}%")

st.divider()

# ── Most Common Error Types ──────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🔁 Most Common Errors")
    error_counts = df["error_type"].value_counts().reset_index()
    error_counts.columns = ["Error Type", "Count"]
    st.bar_chart(error_counts.set_index("Error Type"))

with col_right:
    st.subheader("✅ Fix Success by Error Type")
    success_rate = df.groupby("error_type")["success"].mean() * 100
    success_rate = success_rate.reset_index()
    success_rate.columns = ["Error Type", "Success Rate (%)"]
    st.bar_chart(success_rate.set_index("Error Type"))

st.divider()

# ── Time Saved Estimate ──────────────────────────────────────────────
st.subheader("⏱️ Estimated Time Saved")
avg_minutes_per_incident = 45
time_saved = succeeded * avg_minutes_per_incident
st.metric(
    "Total time saved",
    f"{time_saved} minutes",
    delta=f"{succeeded} incidents auto-resolved"
)

st.divider()

# ── Full History Table ───────────────────────────────────────────────
st.subheader("📜 Full Fix History")
df["Status"] = df["success"].apply(lambda x: "✅ Fixed" if x else "❌ Failed")
df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")

st.dataframe(
    df[["timestamp", "error_type", "root_cause", "fix_command", "Status"]].rename(columns={
        "timestamp":  "Time",
        "error_type": "Error Type",
        "root_cause": "Root Cause",
        "fix_command": "Fix Command",
    }),
    use_container_width=True
)