import json
import re

def parse_llm_output(text: str) -> dict:
    try:
        clean_text = re.sub(r"```json\s*|\s*```", "", text.strip())
        return json.loads(clean_text)
    except Exception as e:
        return {"error": f"Failed to parse JSON: {str(e)}", "raw": text}

def evaluate_response(response: dict):
    score = 0
    checks = []
    response=parse_llm_output(response)
    #check summary
    summary = response.get("summary", "")
    if summary and len(summary.split()) >= 10:
        score += 15
        checks.append(("summary", True, "Present and meaningful"))
    else:
        checks.append(("summary", False, "Missing or too short"))

    #check primary driver
    primary_driver = response.get("primary_driver", "")
    if primary_driver and len(primary_driver.strip()) > 10:
        score += 15
        checks.append(("primary_driver", True, "Driver identified"))
    else:
        checks.append(("primary_driver", False, "Missing or vague"))

    #check causal chain-----important 
    chain = response.get("causal_chain", [])
    if isinstance(chain, list) and len(chain) >= 3:
        score += 25
        checks.append(("causal_chain", True, f"{len(chain)} steps found in chain"))
    else:
        checks.append(("causal_chain", False, "Chain is missing or has less than 3 steps"))

    #check conflicting signals
    conflicts = response.get("conflicting_signals", "")
    if conflicts and len(conflicts.split()) >= 5:
        score += 15
        checks.append(("conflicting_signals", True, "Conflict acknowledged"))
    else:
        checks.append(("conflicting_signals", False, "No conflict reasoning found"))

    #check key risk----must be present
    key_risk = response.get("key_risk", "")
    if key_risk and len(key_risk.strip()) > 10:
        score += 15
        checks.append(("key_risk", True, "Risk identified"))
    else:
        checks.append(("key_risk", False, "Missing"))

    #check actionable recommendations
    action = response.get("action", "")
    if action and len(action.split()) >= 8:
        score += 10
        checks.append(("action", True, "Actionable suggestion present"))
    else:
        checks.append(("action", False, "Missing or too vague"))

    #check number
    text = str(response)
    if any(char.isdigit() for char in text):
        score += 5
        checks.append(("Uses numbers", True, "Reasoning contains numbers"))
    else:
        checks.append(("Uses numbers", False, "Reasoning contains no numbers"))

    #here lmm will give its own score 
    llm_score= response.get("self_score", "0")
    try:
        llm_score = int(llm_score)
    except:
        llm_score = 0
    
    mixed_score = int((score + llm_score) / 2) if llm_score > 0 else score
    
    if mixed_score >= 80:
        grade = "EXCELLENT"
    elif mixed_score >= 60:
        grade = "GOOD"
    else:
        grade = "POOR"

    return {
        "rule_score": score,
        "llm_score": llm_score,
        "mixed_score": mixed_score,
        "score": mixed_score,
        "grade": grade,
        "checks": checks
    }