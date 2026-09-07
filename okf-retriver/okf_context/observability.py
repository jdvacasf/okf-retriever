import logging


logger = logging.getLogger("okf_context")


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level)
