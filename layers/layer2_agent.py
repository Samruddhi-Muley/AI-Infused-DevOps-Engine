from memory.db import lookup_past_fix

def decide_strategy(diagnosis: dict) -> dict:
    confidence = diagnosis.get("confidence", 0.0)
    error_type = diagnosis.get("error_type", "unknown")
    is_file_edit = diagnosis.get("is_file_edit", False)
    fix_command = diagnosis.get("suggested_fix", "")

    # Build a specific key for memory lookup
    # e.g. "module_not_found::matplotlib" instead of just "module_not_found"
    error_key = error_type
    if error_type == "module_not_found" and fix_command:
        # Extract package name from "pip install matplotlib"
        parts = fix_command.strip().split()
        if len(parts) >= 3 and parts[0] == "pip" and parts[1] == "install":
            error_key = f"module_not_found::{parts[2]}"

    if is_file_edit:
        return {
            "strategy": "escalate",
            "fix_command": None,
            "reason": f"Fix requires editing a source file manually: {diagnosis.get('fix_explanation', '')}",
            "past_fix_found": False
        }

    past_fix = lookup_past_fix(error_type, error_key)

    if past_fix and past_fix["success"]:
        strategy = "use_past_fix"
        fix_to_use = past_fix["fix_command"]
        reason = f"Used previously successful fix for '{error_key}'"
    elif confidence >= 0.85:
        strategy = "auto_fix"
        fix_to_use = diagnosis["suggested_fix"]
        reason = f"High confidence ({confidence:.0%}). Executing automatically."
    elif 0.5 <= confidence < 0.85:
        strategy = "cautious_fix"
        fix_to_use = diagnosis["suggested_fix"]
        reason = f"Medium confidence ({confidence:.0%}). Will validate after fix."
    else:
        strategy = "escalate"
        fix_to_use = None
        reason = f"Low confidence ({confidence:.0%}). Human review needed."

    return {
        "strategy": strategy,
        "fix_command": fix_to_use,
        "reason": reason,
        "past_fix_found": past_fix is not None
    }