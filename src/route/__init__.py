from src.env import MIYOUSHE, HOYOLAB


def get_routes():
    from .error import validation_exception_handler

    routes = [
        validation_exception_handler,
    ]

    if MIYOUSHE:
        from .article import parse_article

        routes.append(parse_article)
    if HOYOLAB:
        from .article_hoyolab import parse_hoyo_article

        routes.append(parse_hoyo_article)
