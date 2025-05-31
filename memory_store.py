import sqlite3
import uuid
from datetime import datetime
import json

class MemoryStore:
    def __init__(self, db_path="memory_store.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS memory_log (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    source TEXT,
                    sender TEXT,
                    conversation_id TEXT,
                    data TEXT
                )
            ''')

    def reset_table(self):
        with self.conn:
            self.conn.execute('DROP TABLE IF EXISTS memory_log')
        self._create_table()
        print("[MemoryStore] memory_log table reset (dropped and recreated).")

    def log(self, source, data, sender=None, conversation_id=None):
        entry_id = str(uuid.uuid4())
        timestamp = str(datetime.now())
        data_json = json.dumps(data)

        with self.conn:
            self.conn.execute('''
                INSERT INTO memory_log (id, timestamp, source, sender, conversation_id, data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (entry_id, timestamp, source, sender, conversation_id, data_json))

        print(f"[Memory Log] Added entry: {{'id': '{entry_id}', 'timestamp': '{timestamp}', 'source': '{source}', 'sender': '{sender}', 'conversation_id': '{conversation_id}', 'data': {data}}}")

    def add_entry(self, source, data, sender=None, conversation_id=None):
        self.log(source, data, sender, conversation_id)

    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, timestamp, source, sender, conversation_id, data FROM memory_log')
        rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "timestamp": row[1],
                "source": row[2],
                "sender": row[3],
                "conversation_id": row[4],
                "data": json.loads(row[5])
            })
        cursor.close()
        return result

    def close(self):
        if self.conn:
            self.conn.close()

    def __del__(self):
        self.close()
