def get_routes():
    from .article import parse_article
    from .error import validation_exception_handler

    return [
        parse_article,
        validation_exception_handler,
    ]
