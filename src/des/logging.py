import logging

from rich.logging import RichHandler

log = logging.getLogger(__spec__.parent)
log.setLevel(logging.DEBUG)
log.addHandler(RichHandler())
