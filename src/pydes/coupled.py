from collections.abc import Set

from pydes.model import Model


class Coupled(Model):
    components: Set[Model]
