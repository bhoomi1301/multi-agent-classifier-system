# rfq_agent.py
def process_rfq(payload, memory):
    missing_fields = []
    anomalies = []

    required_fields = ["rfq_id", "client_name", "product", "quantity", "deadline"]

    for field in required_fields:
        if field not in payload or payload[field] in [None, ""]:
            missing_fields.append(field)

    quantity = payload.get("quantity")
    if quantity is not None:
        if not isinstance(quantity, int):
            anomalies.append("Quantity not an integer")
        elif quantity <= 0:
            anomalies.append("Quantity not positive")
    else:
        anomalies.append("Quantity missing")

    # Additional validation can be added here (e.g., date format check for deadline)

    result = {
        "missing_fields": missing_fields,
        "anomalies": anomalies,
        "processed_data": payload
    }

    memory.log("RFQ", result)
    return result





