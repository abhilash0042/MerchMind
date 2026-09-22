import os
import re
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_supabase: Client = None

# Regex for validating UUID v4 format
_UUID_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)


def _is_valid_uuid(value: str) -> bool:
    """Check if a string is a valid UUID format."""
    return bool(value and _UUID_RE.match(value))


def get_supabase_client() -> Client:
    global _supabase
    if _supabase is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        _supabase = create_client(url, key)
    return _supabase

def fetch_recent_context(seller_id: str, limit: int = 10) -> str:
    """
    Fetches the most recent product summaries from the product_embeddings table
    to give the AI Agent real context.
    
    Validates seller_id as a proper UUID before querying to prevent
    Postgres 22P02 errors ('invalid input syntax for type uuid').
    """
    # ── Guard: validate UUID format before touching the DB ──
    if not _is_valid_uuid(seller_id):
        return f"Skipped Supabase fetch: seller_id '{seller_id}' is not a valid UUID."

    try:
        supabase = get_supabase_client()
        response = supabase.table("product_embeddings") \
            .select("summary_text, metadata, embed_date") \
            .eq("seller_id", seller_id) \
            .order("embed_date", desc=True) \
            .limit(limit) \
            .execute()
            
        data = response.data
        if not data:
            return "No recent product embeddings found for this seller."
            
        context_items = []
        for item in data:
            context_items.append(f"[{item['embed_date']}] {item['summary_text']}")
            
        return "\n".join(context_items)
    except Exception as e:
        print(f"  ⚠️ Supabase context fetch error: {e}")
        return "Failed to fetch context from database."
