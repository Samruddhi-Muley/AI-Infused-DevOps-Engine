import streamlit as st
import sqlite3
import pandas as pd
from memory.db import DB_PATH

st.set_page_config(page_title="AIDE Dashboard", page_icon="📊", layout="wide")
st.title("📊 AIDE Analytics Dashboard")
st.caption("Real-time insights from your self-healing DevOps engine.")

# ── Load Data ────────────────────────────────────────────────────────
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
time_saved = succeeded * 45  # avg 45 mins saved per auto-fix

st.subheader("🔢 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Attempts",  total)
col2.metric("Successful",      f"{succeeded} ✅")
col3.metric("Failed",          f"{failed} ❌")
col4.metric("Success Rate",    f"{rate:.1f}%")
col5.metric("Time Saved",      f"{time_saved} mins")

st.divider()

# ── Charts ───────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🔁 Most Common Error Types")
    error_counts = df["error_type"].value_counts().reset_index()
    error_counts.columns = ["Error Type", "Count"]
    st.bar_chart(error_counts.set_index("Error Type"))

with col_right:
    st.subheader("✅ Success Rate by Error Type")
    success_rate = df.groupby("error_type")["success"].mean() * 100
    success_rate = success_rate.reset_index()
    success_rate.columns = ["Error Type", "Success Rate (%)"]
    st.bar_chart(success_rate.set_index("Error Type"))

st.divider()

# ── Strategy Breakdown ───────────────────────────────────────────────
st.subheader("🤔 Fix Strategy Breakdown")

auto_fixed    = len(df[df["fix_command"].str.startswith("pip", na=False)])
port_fixed    = len(df[df["error_type"] == "port_conflict"])
escalated     = failed
syntax_errors = len(df[df["error_type"] == "syntax_error"])

s_col1, s_col2, s_col3, s_col4 = st.columns(4)
s_col1.metric("Auto Fixed",     auto_fixed,    delta="no human needed")
s_col2.metric("Port Fixes",     port_fixed,    delta="process killed")
s_col3.metric("Escalated",      escalated,     delta="needed human")
s_col4.metric("Syntax Errors",  syntax_errors, delta="code edits needed")

st.divider()

# ── Full History Table ───────────────────────────────────────────────
st.subheader("📜 Full Fix History")

df["Status"] = df["success"].apply(lambda x: "✅ Fixed" if x else "❌ Failed")
df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")

st.dataframe(
    df[["timestamp", "error_type", "root_cause", "fix_command", "Status"]].rename(columns={
        "timestamp":   "Time",
        "error_type":  "Error Type",
        "root_cause":  "Root Cause",
        "fix_command": "Fix Command",
    }),
    use_container_width=True
)

st.divider()

# ── Clear History Button ─────────────────────────────────────────────
st.subheader("⚙️ Manage Data")
if st.button("🗑️ Clear Fix History", type="secondary"):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM fix_history")
    conn.commit()
    conn.close()
    st.success("History cleared!")
    st.rerun()