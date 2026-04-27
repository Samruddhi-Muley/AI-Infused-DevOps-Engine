import streamlit as st
from memory.db import init_db, get_all_history
from layers.layer1_genai import diagnose_log
from layers.layer2_agent import decide_strategy
from layers.layer3_executor import run_fix

# Initialize DB on startup
init_db()

st.set_page_config(page_title="AIDE — AI DevOps Engine", page_icon="🤖", layout="wide")
st.title("🤖 AIDE — AI-Infused DevOps Engine")
st.caption("Paste a failed build or deployment log. AIDE will diagnose, decide, and fix it.")

# ── Sidebar: History ────────────────────────────────────────────────
with st.sidebar:
    st.header("📜 Fix History")
    history = get_all_history()
    if history:
        for row in history:
            icon = "✅" if row[4] else "❌"
            st.markdown(f"{icon} **{row[1]}** — `{row[3][:40]}...`")
            st.caption(row[5])
    else:
        st.info("No fixes yet.")

# ── Main: Log Input ─────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    log_input = st.text_area(
        "Paste your error log here:",
        height=250,
        placeholder='e.g. ModuleNotFoundError: No module named "pandas"'
    )

with col2:
    st.subheader("⚙️ Settings")
    auto_execute = st.toggle("Allow auto-execution", value=True)
    show_raw = st.toggle("Show raw diagnosis JSON", value=False)
    validation_cmd = st.text_input(
        "Validation command (optional):",
        placeholder="e.g. python -c 'import pandas'"
    )

run_btn = st.button("🚀 Run AIDE", type="primary", disabled=not log_input.strip())

# ── Pipeline ────────────────────────────────────────────────────────
if run_btn and log_input.strip():

    st.divider()

    # Layer 1: Diagnosis
    with st.spinner("🧠 Layer 1 — Diagnosing with Groq (Llama 3.3 70B)..."):
        try:
            diagnosis = diagnose_log(log_input)
        except Exception as e:
            st.error(f"Diagnosis failed: {e}")
            st.stop()

    st.subheader("🧠 Layer 1 — Diagnosis")
    d_col1, d_col2, d_col3 = st.columns(3)
    d_col1.metric("Error Type", diagnosis.get("error_type", "unknown"))
    d_col2.metric("Confidence", f"{diagnosis.get('confidence', 0):.0%}")
    d_col3.metric("Suggested Fix", diagnosis.get("suggested_fix", "")[:30] + "...")

    st.info(f"**Root Cause:** {diagnosis.get('root_cause', '')}")

    if show_raw:
        st.json(diagnosis)

    # Layer 2: Agent decision
    with st.spinner("🤔 Layer 2 — Agent deciding strategy..."):
        decision = decide_strategy(diagnosis)

    st.subheader("🤔 Layer 2 — Agent Decision")

    strategy = decision["strategy"]

    if decision["past_fix_found"]:
        st.success("💾 Found a past successful fix in memory!")

    if strategy == "escalate":
        st.warning(f"⚠️ **Escalating to human.** {decision['reason']}")
        st.markdown(f"**Suggested fix for review:** `{diagnosis.get('suggested_fix', 'N/A')}`")
        st.stop()

    st.info(f"**Strategy:** `{strategy}` — {decision['reason']}")
    st.code(decision["fix_command"], language="bash")

    # Layer 3: Execution
    if not auto_execute and strategy != "use_past_fix":
        st.warning("Auto-execution is disabled. Toggle it on to run fixes.")
        st.stop()

    with st.spinner("🔧 Layer 3 — Executing fix..."):
        exec_result = run_fix(
            fix_command=decision["fix_command"],
            error_type=diagnosis["error_type"],
            root_cause=diagnosis["root_cause"]
        )

    st.subheader("🔧 Layer 3 — Execution Result")

    if exec_result["success"]:
        st.success(f"✅ Fix applied successfully! (Attempt {exec_result['attempt']})")
    else:
        st.error(f"❌ Fix failed after {exec_result['attempt']} attempt(s). Human escalation needed.")

    if exec_result["stdout"]:
        with st.expander("stdout"):
            st.code(exec_result["stdout"])
    if exec_result["stderr"]:
        with st.expander("stderr"):
            st.code(exec_result["stderr"])

    # Validation (optional)
    if validation_cmd and exec_result["success"]:
        from layers.layer3_executor import validate_fix

        with st.spinner("🔍 Running validation..."):
            valid = validate_fix(validation_cmd)
        if valid:
            st.success("✅ Validation passed! Fix confirmed working.")
        else:
            st.warning("⚠️ Validation failed. May need manual review.")

    # GitHub Actions snippet
    st.subheader("🔗 CI/CD Integration")
    st.markdown("Add AIDE to your GitHub Actions pipeline:")
    st.code("""
name: CI with AIDE
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run build
        id: build
        run: your-build-command
        continue-on-error: true
      - name: Run AIDE on failure
        if: steps.build.outcome == 'failure'
        run: |
          pip install -r requirements.txt
          python -c "
from layers.layer1_genai import diagnose_log
from layers.layer2_agent import decide_strategy
from layers.layer3_executor import run_fix
log = open('build.log').read()
d = diagnose_log(log)
dec = decide_strategy(d)
run_fix(dec['fix_command'], d['error_type'], d['root_cause'])
"
    """, language="yaml")