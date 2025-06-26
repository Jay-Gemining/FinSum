import datetime

# 简单的内存缓存
_cache = {}
CACHE_EXPIRY_HOURS = 6  # 缓存过期时间（小时）

def set_cached_report(report_date_str: str, report_data: dict):
    """
    将报告数据连同时间戳一起存储在缓存中。
    report_date_str 用作缓存键的一部分，以确保每日刷新。
    """
    timestamp = datetime.datetime.now()
    _cache[report_date_str] = {"data": report_data, "timestamp": timestamp}
    print(f"报告 {report_date_str} 已于 {timestamp} 缓存")

def get_cached_report(report_date_str: str) -> dict | None:
    """
    如果缓存中存在且未过期的报告数据，则从中检索。
    检查缓存是否针对当前的 report_date_str。
    """
    cached_item = _cache.get(report_date_str)

    if not cached_item:
        return None

    # 检查缓存是否比 CACHE_EXPIRY_HOURS 更旧
    # 或者自上次更新缓存以来美国市场是否已收盘
    # （简化检查：如果基于美国市场收盘时间是新的一天，则认为已过期）
    now = datetime.datetime.now()
    cache_timestamp = cached_item["timestamp"]

    if (now - cache_timestamp).total_seconds() > CACHE_EXPIRY_HOURS * 3600:
        print(f"针对 {report_date_str} 的缓存因时间限制已过期。")
        return None

    # 用于检查美国市场收盘时间的占位符。
    # 对于 MVP，我们可以依赖 CACHE_EXPIRY_HOURS 和每日密钥。
    # 更可靠的检查将涉及市场交易时间和时区。
    # 示例：if cache_timestamp.date() < now.date() and now.hour > 16 (大约在美国东部时间下午 4 点之后):
    # return None

    print(f"针对 {report_date_str} 的缓存命中")
    return cached_item["data"]

def clear_cache():
    """清除整个缓存。"""
    global _cache
    _cache = {}
    print("缓存已清除。")
