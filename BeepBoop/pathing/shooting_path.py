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
            # Find intersection of the car direction and the desired ball direction to find intermediate point for bezier curve.
            yaw = packet.game_cars[self.agent.index].physics.rotation.yaw
            car_dir: Vector3 = Vector3(math.cos(yaw), math.sin(yaw), 0)
            desired_bal_dir: Vector3 = Vector3(self.agent.game_info.their_goal.center).modified(z=ball.z) - ball
            intermediate: Vector3 = calculations.line_line_intersection(car, car + car_dir, ball, desired_bal_dir)
            self.path = pathing.quadratic_bezier(car, intermediate, ball)

            color = self.agent.renderer.red() if self.agent.team else self.agent.renderer.cyan()
            self.agent.renderer.draw_line_3d(car, intermediate, color)
            self.agent.renderer.draw_line_3d(intermediate, ball, color)
            self.agent.renderer.draw_string_3d(car, 1, 1, "P0", color)
            self.agent.renderer.draw_string_3d(intermediate, 1, 1, "P1", color)
            self.agent.renderer.draw_string_3d(ball, 1, 1, "P2", color)

        return self.path
