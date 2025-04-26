from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.engine import Engine
    from engine.entity import Entity


class BaseComponent:
    entity: Entity  # Owning entity instance.

    @property
    def engine(self) -> Engine:
        return self.entity.gamemap.engine