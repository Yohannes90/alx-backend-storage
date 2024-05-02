#!/usr/bin/env python3
"""  obtain the HTML content of a particular URL using requests module
"""
import requests
import redis


def get_page(url: str) -> str:
    """Fetches the HTML content of a URL and caches it"""
    redis_conn = redis.Redis()
    url_count_key = f"count:{url}"
    redis_conn.incr(url_count_key)
    cached_content = redis_conn.get(url)
    if cached_content:
        return cached_content.decode("utf-8")
    response = requests.get(url)
    html_content = response.text
    redis_conn.setex(url, 10, html_content)
    return html_content


url = "http://slowwly.robertomurray.co.uk"
print(get_page(url))
