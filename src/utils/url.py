from typing import Dict

from urlextract import URLExtract
from httpx import URL

from src.env import HOYOLAB_HOST, MIYOUSHE_HOST

extractor = URLExtract()


def parse_link(url: URL) -> URL:
    host = HOYOLAB_HOST
    if "miyoushe" in url.host:
        host = MIYOUSHE_HOST

    if url.fragment:
        path = ""
        if url.path != "/":
            path = url.path
        new_url = URL(f"https://a{path}{url.fragment}")
        return url.copy_with(host=host, path=new_url.path, fragment=None, query=None)

    return url.copy_with(host=host)


def get_lab_link(url: str) -> Dict[str, str]:
    data = {}
    for old_url in extractor.find_urls(url):
        u = URL(old_url)
        if u.scheme not in ["http", "https"]:
            continue
        if u.host not in [
            "www.miyoushe.com",
            "m.miyoushe.com",
            "www.hoyolab.com",
            "m.hoyolab.com",
        ]:
            continue
        parsed_link = str(parse_link(u))
        if "article" in parsed_link:
            data[old_url] = parsed_link
    return data
