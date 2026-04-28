import sys
import json
from layers.layer1_genai import diagnose_log
from layers.layer2_agent import decide_strategy
from layers.layer3_executor import run_fix
from memory.db import init_db

def main():
    init_db()

    if len(sys.argv) < 2:
        print("Usage: python aide_runner.py <log_file>")
        sys.exit(1)

    log_file = sys.argv[1]

    try:
        with open(log_file, "r") as f:
            log_text = f.read()
    except FileNotFoundError:
        print(f"Log file not found: {log_file}")
        sys.exit(1)

    print("\n🧠 Layer 1 — Diagnosing...")
    try:
        diagnosis = diagnose_log(log_text)
    except Exception as e:
        print(f"Diagnosis failed: {e}")
        sys.exit(1)

    print(json.dumps(diagnosis, indent=2))

    print("\n🤔 Layer 2 — Deciding strategy...")
    decision = decide_strategy(diagnosis)
    print(f"Strategy : {decision['strategy']}")
    print(f"Reason   : {decision['reason']}")

    if decision["strategy"] == "escalate":
        print("\n⚠️ Escalating to human. No command executed.")
        print(f"Suggested fix for review: {diagnosis.get('fix_explanation', 'N/A')}")
        sys.exit(1)

    print(f"\n🔧 Layer 3 — Executing fix...")
    print(f"Command: {decision['fix_command']}")

    result = run_fix(
        fix_command=decision["fix_command"],
        error_type=diagnosis["error_type"],
        root_cause=diagnosis["root_cause"]
    )

    if result["success"]:
        print("\n✅ Fix applied successfully!")
        sys.exit(0)
    else:
        print("\n❌ Fix failed. Human intervention needed.")
        print(result["stderr"])
        sys.exit(1)

if __name__ == "__main__":
    main()