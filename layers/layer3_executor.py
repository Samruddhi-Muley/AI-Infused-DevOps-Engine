import subprocess
from memory.db import save_fix

MAX_RETRIES = 2
TIMEOUT = 30  # seconds


def run_fix(fix_command: str, error_type: str, root_cause: str) -> dict:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = subprocess.run(
                fix_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=TIMEOUT
            )

            success = result.returncode == 0

            save_fix(
                error_type=error_type,
                root_cause=root_cause,
                fix_command=fix_command,
                success=success
            )

            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "attempt": attempt,
                "status": "fixed" if success else "failed"
            }

        except subprocess.TimeoutExpired:
            if attempt == MAX_RETRIES:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Timed out after {TIMEOUT}s",
                    "attempt": attempt,
                    "status": "timeout"
                }


def validate_fix(validation_command: str) -> bool:
    try:
        result = subprocess.run(
            validation_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=TIMEOUT
        )
        return result.returncode == 0
    except Exception:
        return False