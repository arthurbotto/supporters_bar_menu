class AdminLogRepository:

    def __init__(self, connection):
        self._connection = connection
    
    def log(self, action, entity_type, entity_id, entity_name, detail=None):
        rows = self._connection.execute(
            """INSERT INTO admin_logs (action, entity_type, entity_id, entity_name, detail)
                VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                [action, entity_type, entity_id, entity_name, detail]
        )
        return rows[0]["id"]
    
    def all_logs(self, limit=200):
        rows = self._connection.execute("SELECT * FROM admin_logs ORDER BY created_at DESC LIMIT %s", [limit])
        return rows