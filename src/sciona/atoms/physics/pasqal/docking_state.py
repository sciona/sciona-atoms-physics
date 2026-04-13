from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    import networkx as nx


class MolecularDockingState(BaseModel):
    """State for Pasqal-inspired molecular docking."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    graph: "nx.Graph | None" = Field(default=None)
    lattice: "nx.Graph | None" = Field(default=None)
    lattice_id_coord_dic: dict[int, tuple[float, float]] | None = Field(default=None)
