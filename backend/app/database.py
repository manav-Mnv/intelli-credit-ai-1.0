from supabase import create_client, Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)

_supabase_client: Client = None


def get_supabase() -> Client:
    """Get or create Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase credentials not configured — running in demo mode")
            return None
        try:
            _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            return None
    return _supabase_client


async def insert_record(table: str, data: dict) -> dict | None:
    """Insert a record into a Supabase table."""
    client = get_supabase()
    if not client:
        logger.info(f"[Demo Mode] Would insert into {table}: {data}")
        return {**data, "id": "demo-uuid"}
    try:
        result = client.table(table).insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Insert to {table} failed: {e}")
        return None


async def fetch_record(table: str, filters: dict) -> list:
    """Fetch records from a Supabase table with filters."""
    client = get_supabase()
    if not client:
        return []
    try:
        query = client.table(table).select("*")
        for key, val in filters.items():
            query = query.eq(key, val)
        result = query.execute()
        return result.data or []
    except Exception as e:
        logger.error(f"Fetch from {table} failed: {e}")
        return []


async def update_record(table: str, record_id: str, data: dict) -> dict | None:
    """Update a record in a Supabase table."""
    client = get_supabase()
    if not client:
        return data
    try:
        result = client.table(table).update(data).eq("id", record_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Update {table} record {record_id} failed: {e}")
        return None
