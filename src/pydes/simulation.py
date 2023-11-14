from uuid import UUID

import networkx as nx

from .core import Field, Immutable, model_id


class Simulation(Immutable):
    """The global instantiator for a simulation"""

    id: UUID = Field(default_factory=model_id)
    graph: nx.DiGraph = Field(default_factory=nx.DiGraph)
    num_processes: int = Field(default=1)
    num_threads: int = Field(default=1)

    def build_model_graph(self):
        ...
