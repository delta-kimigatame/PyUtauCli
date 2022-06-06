import logging

def get_logger(module: str, verbose: bool) -> logging.Logger:
    logger = logging.getLogger(module)
    logger = _set_handler(logger, logging.StreamHandler(), False)
    logger = _set_handler(logger, logging.FileHandler("log.txt", encoding="utf-8"), verbose)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    return logger


def _set_handler(logger: logging.Logger, handler: logging.Handler, verbose: bool) -> logging.Logger:
    if verbose:
        handler.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(asctime)s %(name)s:%(lineno)s %(funcName)s [%(levelname)s]: %(message)s'))
    logger.addHandler(handler)
    return logger
