import logging
import sys

logger = logging.getLogger("fii-crawler")
logging.getLogger("chardet.charsetprober").disabled = True

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
