import logging

logging.basicConfig(
    encoding="utf-8",
    format="%(levelname)7s:%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.WARNING,
    force=True,
)
logger = logging.getLogger()
