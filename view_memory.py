from memory_store import MemoryStore

store = MemoryStore()
for entry in store.get_all():
    print(entry)
