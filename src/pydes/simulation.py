from uuid import UUID

import networkx as nx


class Simulation:
    """The global instantiator for a simulation"""

    id: UUID
    graph: nx.DiGraph

    def __init__(self):
        self.graph = nx.DiGraph()
