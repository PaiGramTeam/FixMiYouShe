from typing import Dict

from urlextract import URLExtract
from httpx import URL

extractor = URLExtract()
MIYOUSHE_HOST = "www.miyoushe.pp.ua"
HOYOLAB_HOST = "www.hoyolab.pp.ua"


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
    for url in extractor.find_urls(url):
        u = URL(url)
        if u.scheme not in ["http", "https"]:
            continue
        if u.host not in ["www.miyoushe.com", "m.miyoushe.com", "www.hoyolab.com", "m.hoyolab.com"]:
            continue
        data[url] = str(parse_link(u))
    return data
