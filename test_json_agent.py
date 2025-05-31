from json_agent import JSONAgent
from memory_store import MemoryStore

sample_json = {
    "invoice_id": "INV-2025-0017",
    "amount": 0,  # anomaly
    "vendor": "TechParts Ltd.",
    "date": "2025-05-30"
}

memory = MemoryStore()
agent = JSONAgent(memory)

result = agent.process_json(sample_json)

print("\nProcessed JSON Output:")
print(result)

print("\nMemory Log:")
print(memory.get_all())
