import platform

OS_TYPE = platform.system()  # 'Windows', 'Linux', or 'Darwin'

def get_diagnosis_prompt(log_text: str) -> str:
    return f"""You are an expert DevOps engineer working on a {OS_TYPE} machine.
Analyze the following build/deployment error log and return ONLY a valid JSON object.
No markdown, no backticks, no explanation — just the raw JSON.

Error Log:
{log_text}

Return exactly this JSON structure:
{{
  "error_type": "short_snake_case_category",
  "root_cause": "plain English explanation of what went wrong",
  "suggested_fix": "a single executable terminal command only, no English sentences",
  "fix_explanation": "human readable explanation of what the fix does",
  "confidence": 0.95,
  "is_file_edit": false
}}

RULES for suggested_fix:
- Missing package: pip install <package_name>
- Port conflict on Windows: python -c "import psutil; [p.kill() for p in psutil.process_iter() if any(c.laddr.port == <PORT> for c in p.net_connections())]"
- Port conflict on Linux/Mac: kill $(lsof -t -i:<PORT>)
- Permission error on Windows: icacls <path> /grant Everyone:F
- Permission error on Linux/Mac: chmod 755 <path>
- Syntax errors or code fixes: set is_file_edit to true
- confidence must be a float between 0.0 and 1.0
"""