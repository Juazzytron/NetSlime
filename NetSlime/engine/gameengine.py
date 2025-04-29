from __future__ import annotations

from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.map import compute_fov

from engine import exceptions


from engine.inputhandlers import MainGameEventHandler
from render.messagelog import MessageLog
from render.renderfunctions import render_bar, render_names_at_mouse_location

if TYPE_CHECKING:
    from engine.entity import Entity, Actor
    from engine.gamemap import GameMap
    from engine.inputhandlers import EventHandler


class Engine:
    game_map: GameMap

    def __init__(self, player: Actor):
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.message_log= MessageLog()
        self.mouse_location = (0, 0)
        self.player = player

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass  # Ignore impossible action exceptions from AI.

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
            )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        screen_width, screen_height = console.width, console.height
        map_height = self.game_map.height

        # Calculate the dynamic Y-positions
        hp_bar_height = 1  # HP bar takes up 1 line
        message_log_height = 5  # Message log takes up 5 lines

        # Position the message log above the HP bar, ensuring they stay within bounds
        message_log_y = screen_height - hp_bar_height - message_log_height
        hp_bar_y = screen_height - hp_bar_height

        # Make sure the map is not obstructed
        self.game_map.render(console)

        # Render the message log at the calculated position
        self.message_log.render(console=console, x=0, y=message_log_y, width=screen_width, height=message_log_height)

        # Render the HP bar just above the message log
        render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=40,
            y=hp_bar_y
        )
        render_names_at_mouse_location(console=console, x=21, y=44, engine=self)
