from memory_store import MemoryStore

memory = MemoryStore()
memory.reset_table()  # This will drop and recreate your table with the updated schema
