from abc import ABCMeta, abstractmethod
from typing import List, Optional

from rlbot.utils.structures.game_data_struct import GameTickPacket

from beepboop import BeepBoop
from bot_math.Vector3 import Vector3


class BasePath(metaclass=ABCMeta):
    def __init__(self, agent: BeepBoop):
        self.agent: BeepBoop = agent
        self.path: List[Vector3] = []

    def closest_point_on_path(self) -> Vector3:
        """
        Determines the point on the path that the agent is closest to.

        :return: Point on the path that the agent is closest to
        """

        closest_dist: float = float("infinity")
        closest_point: Optional[Vector3] = None
        position: Vector3 = Vector3(self.agent.game_info.my_car.pos)

        for point in self.path:
            current_dist: float = Vector3.distance(point, position)
            if current_dist < closest_dist:
                closest_dist = current_dist
                closest_point = point

        if closest_point is None:
            raise Exception("Closest point was None. self.path could be empty.")
        return closest_point

    def remove_points_to_index(self, i: int) -> None:
        """
        Removes all the points in self.path, up to and including self.path[``i``].
        """
        for _ in range(i + 1):
            self.path.pop(0)

    def draw_path(self) -> None:
        """
        Renders ``self.path`` on-screen.
        """
        if self.path:
            color = self.agent.renderer.red() if self.agent.team else self.agent.renderer.cyan()
            self.agent.renderer.draw_polyline_3d(self.path, color)

    @abstractmethod
    def generate_path(self, packet: GameTickPacket) -> List[Vector3]:
        pass
