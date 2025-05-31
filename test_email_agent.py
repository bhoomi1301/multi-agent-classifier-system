from email_agent import EmailAgent
from memory_store import MemoryStore

# Sample email
sample_email = """
From: urgent.buyer@company.com
To: sales@vendor.com
Subject: Immediate Request

Hi team,

This is urgent. We need 500 aluminum sheets quoted ASAP.

Thanks,
Procurement Lead
"""

memory = MemoryStore()
agent = EmailAgent(memory)

result = agent.process_email(sample_email)

print("\nCRM Output:")
print(result)

print("\nFull Memory Log:")
print(memory.get_all())
