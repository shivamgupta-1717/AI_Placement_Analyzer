import json
from sqlalchemy import TypeDecorator, Text
from app.config import settings

def get_vector_column_type(dimension: int = 768):
    """
    Returns native pgvector.sqlalchemy.Vector if connecting to PostgreSQL,
    or a JSON/Text TypeDecorator if running on SQLite / fallback.
    """
    if "postgresql" in settings.DATABASE_URL:
        try:
            from pgvector.sqlalchemy import Vector
            return Vector(dimension)
        except ImportError:
            pass

    class SQLiteVector(TypeDecorator):
        impl = Text
        cache_ok = True

        def process_bind_param(self, value, dialect):
            if value is None:
                return None
            if isinstance(value, (list, tuple)):
                return json.dumps(list(value))
            return value

        def process_result_value(self, value, dialect):
            if value is None:
                return None
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except Exception:
                    return []
            return value

    return SQLiteVector
