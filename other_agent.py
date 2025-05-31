# other_agent.py
def process_other(payload, memory):
    # For other or unknown intents, just log with minimal checks
    missing_fields = []
    anomalies = []

    # Optionally, check if "raw_text" or any expected fallback field exists
    if "raw_text" not in payload or not payload["raw_text"]:
        missing_fields.append("raw_text")

    # Add any basic anomaly checks you want here

    result = {
        "missing_fields": missing_fields,
        "anomalies": anomalies,
        "processed_data": payload
    }

    memory.log("Other", result)
    return result



