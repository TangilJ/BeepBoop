import math
from typing import List

from rlbot.utils.structures.game_data_struct import GameTickPacket

from .base_path import BasePath
from bot_math.Vector3 import Vector3
from utils import calculations
import pathing.pathing as pathing


class ShootingPath(BasePath):
    def generate_path(self, packet: GameTickPacket) -> List[Vector3]:
        # TODO: Use future ball predictions and return the first viable one, instead of using the current ball position
        ball = Vector3(packet.game_ball.physics.location)
        return self._generate_path_with_ball_position(packet, ball)

    def _generate_path_with_ball_position(self, packet: GameTickPacket, ball: Vector3) -> List[Vector3]:
        car = Vector3(packet.game_cars[self.agent.index].physics.location)

        if pathing.in_shooting_cone(car, ball, -1 * calculations.sign(self.agent.team)):
            # Car is in the shooting cone, so make a straight path
            self.path = pathing.linear_bezier(car, ball)
        else:
            # If the direction of the car and the desired ball direction are pointing to different sides of the line
            # between the car and the ball, use a quadratic bezier. Else use a cubic bezier.
            # TODO: Implement above check. Using only quadratic bezier curves for now.

            # Quadratic bezier curve
            # p0 = car pos
            # p1 = intermediate point
            # p2 = ball pos
            # Find intersection of the car direction and the desired ball direction to find p1.
            actual_p0p2_dist: float = Vector3.distance(car, ball)

            # Find angle p1p0p2 using cosine rule
            yaw = packet.game_cars[self.agent.index].physics.rotation.yaw
            p0p1: Vector3 = Vector3(math.cos(yaw), math.sin(yaw))  # Car direction
            p0p2: Vector3 = ball - car
            p1p2: Vector3 = Vector3(p0p2.x - p0p1.x, p0p2.y - p0p1.y, 0)
            p0p1_dist: float = p0p1.magnitude()
            p0p2_dist: float = p0p2.magnitude()
            p1p2_dist: float = p1p2.magnitude()
            angle_p1p0p2: float = math.acos((p1p2_dist ** 2 - p0p1_dist ** 2 - p0p2_dist ** 2) / (-2 * p0p1_dist * p0p2_dist))

            # Find angle p1p2p0 using cosine rule
            p2p1: Vector3 = Vector3(self.agent.game_info.their_goal.center) - ball  # Desired ball direction
            p2p0: Vector3 = -p0p2
            p1p0: Vector3 = Vector3(p2p1.x - p2p0.x, p2p1.y - p2p0.y, 0)
            p2p1_dist: float = p2p1.magnitude()
            p2p0_dist: float = p2p0.magnitude()
            p1p0_dist: float = p1p0.magnitude()
            angle_p1p2p0: float = math.acos((p1p0_dist ** 2 - p2p1_dist ** 2 - p2p0_dist ** 2) / (-2 * p2p1_dist * p2p0_dist))

            angle_p0p1p2: float = 180 - angle_p1p0p2 - angle_p1p2p0

            actual_p0p1_dist: float = math.sin(angle_p1p2p0) * actual_p0p2_dist / math.sin(angle_p0p1p2)
            p0p1_normalised: Vector3 = p0p1.normalised()
            actual_p0p1: Vector3 = actual_p0p1_dist * p0p1_normalised
            p1 = car + actual_p0p1

            self.path = pathing.quadratic_bezier(car, p1, ball)

        return self.path
