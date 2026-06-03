import html as html_module
import re
import httpx


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo. No API key required."""
    try:
        with httpx.Client(follow_redirects=True) as client:
            resp = client.post(
                "https://html.duckduckgo.com/html/",
                data={"q": query},
                headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"},
                timeout=15.0,
            )

        results = _parse_ddg_html(resp.text, max_results)

        if not results:
            # Fallback: DuckDuckGo Instant Answer JSON API
            resp2 = client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"},
                timeout=10.0,
            )
            data = resp2.json()
            if data.get("AbstractText"):
                results.append(f"{data['AbstractText']}\n{data.get('AbstractURL', '')}")
            for t in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(t, dict) and t.get("Text"):
                    results.append(f"{t['Text']}\n{t.get('FirstURL', '')}")

        if not results:
            return f"No results found for: {query}"

        return "\n\n---\n\n".join(results[:max_results])

    except httpx.TimeoutException:
        return "Search timed out. Check your internet connection."
    except Exception as e:
        return f"Search failed: {e}"


def _parse_ddg_html(html: str, max_results: int) -> list[str]:
    results = []
    # Extract result blocks (title + url + snippet)
    blocks = re.findall(
        r'class="result__title".*?<a[^>]+href="([^"]*)"[^>]*>(.*?)</a>'
        r'.*?class="result__snippet"[^>]*>(.*?)</a>',
        html,
        re.DOTALL,
    )
    for url, title, snippet in blocks[:max_results]:
        title = html_module.unescape(re.sub(r"<[^>]+>", "", title)).strip()
        snippet = html_module.unescape(re.sub(r"<[^>]+>", "", snippet)).strip()
        if title:
            results.append(f"{title}\n{url}\n{snippet}")
    return results


def fetch_url(url: str, max_chars: int = 8000) -> str:
    """Fetch a URL and return its readable text content."""
    try:
        with httpx.Client(follow_redirects=True) as client:
            resp = client.get(
                url,
                timeout=15.0,
                headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"},
            )

        content_type = resp.headers.get("content-type", "")
        if "text/html" in content_type:
            text = _html_to_text(resp.text)
        else:
            text = resp.text

        if len(text) > max_chars:
            return text[:max_chars] + f"\n\n... (truncated — {len(text)} chars total)"
        return text

    except httpx.TimeoutException:
        return f"Timed out fetching: {url}"
    except Exception as e:
        return f"Error fetching URL: {e}"


def _html_to_text(html: str) -> str:
    # Drop scripts, styles, and head
    html = re.sub(r"<(script|style|head)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # Replace block elements with newlines
    html = re.sub(r"<(br|p|div|li|h[1-6]|tr)[^>]*>", "\n", html, flags=re.IGNORECASE)
    # Strip remaining tags
    html = re.sub(r"<[^>]+>", "", html)
    # Decode entities
    html = html_module.unescape(html)
    # Collapse whitespace while preserving paragraph breaks
    html = re.sub(r"[ \t]+", " ", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()
