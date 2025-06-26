import datetime

# Simple in-memory cache
_cache = {}
CACHE_EXPIRY_HOURS = 6

def set_cached_report(report_date_str: str, report_data: dict):
    """
    Stores the report data in the cache with a timestamp.
    report_date_str is used as part of the cache key to ensure daily refresh.
    """
    timestamp = datetime.datetime.now()
    _cache[report_date_str] = {"data": report_data, "timestamp": timestamp}
    print(f"Report for {report_date_str} cached at {timestamp}")

def get_cached_report(report_date_str: str) -> dict | None:
    """
    Retrieves the report data from cache if it exists and is not expired.
    Checks if the cache is for the current report_date_str.
    """
    cached_item = _cache.get(report_date_str)

    if not cached_item:
        return None

    # Check if cache is older than CACHE_EXPIRY_HOURS
    # or if the US market has closed since the cache was last updated
    # (simplified check: if it's a new day based on US market close, consider it expired)
    now = datetime.datetime.now()
    cache_timestamp = cached_item["timestamp"]

    if (now - cache_timestamp).total_seconds() > CACHE_EXPIRY_HOURS * 3600:
        print(f"Cache for {report_date_str} expired due to time limit.")
        return None

    # Placeholder for checking against US market close time.
    # For MVP, we can rely on the CACHE_EXPIRY_HOURS and the daily key.
    # A more robust check would involve market trading hours and timezones.
    # Example: if cache_timestamp.date() < now.date() and now.hour > 16 (after 4 PM ET approx):
    #     return None

    print(f"Cache hit for {report_date_str}")
    return cached_item["data"]

def clear_cache():
    """Clears the entire cache."""
    global _cache
    _cache = {}
    print("Cache cleared.")
