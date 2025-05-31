# complaint_agent.py
def process_complaint(payload, memory):
    missing_fields = []
    anomalies = []

    required_fields = ["ticket_id", "customer_name", "issue", "reported_date"]

    for field in required_fields:
        if field not in payload or payload[field] in [None, ""]:
            missing_fields.append(field)

    issue = payload.get("issue", "")
    if isinstance(issue, str) and len(issue.strip()) < 10:
        anomalies.append("Issue description too short")

    # Optional: validate date format of reported_date here

    result = {
        "missing_fields": missing_fields,
        "anomalies": anomalies,
        "processed_data": payload
    }

    memory.log("Complaint", result)
    return result



