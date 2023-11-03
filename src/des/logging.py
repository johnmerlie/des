import logging
from rich.logging import RichHandler

log = logging.getLogger(__package__)
log.setLevel(logging.DEBUG)
log.addHandler(RichHandler())
