def evaluate_response(response: str):
    """
    Basic evaluator — checks if the LLM response contains expected output sections.
    Extend this with LLM-as-judge or scoring logic as needed.
    """
    required_sections = ["Summary:", "Primary Driver:", "Causal Chain:", "Key Risk:", "Action:"]
    missing = [s for s in required_sections if s not in response]

    if missing:
        print(f"⚠️  Response is missing sections: {', '.join(missing)}")
    else:
        print("✅  Response passed structure validation.")
