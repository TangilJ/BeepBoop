from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from BeepBoop.steps.base_step import BaseStep
from BeepBoop.utils import calculations
from BeepBoop.utils import steering
from BeepBoop.bot_math.Vector3 import Vector3
import math


class ShotStep(BaseStep):
    def __init__(self, agent: BaseAgent):
        super().__init__(agent)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # ShotStep is similar to Gosling's calcShot's way of taking a shot.
        # See RLBot Start-To-Finish episode 5 (https://youtu.be/GPjrWW9zcRQ) for a good explanation of what this code does.

        bot_location: Vector3 = Vector3(packet.game_cars[self.agent.index].physics.location)
        ball_location: Vector3 = Vector3(packet.game_ball.physics.location)

        enemy_goal_centre: Vector3 = Vector3(self.agent.get_field_info().goals[not self.agent.team].location)
        enemy_goal_left: Vector3 = Vector3(enemy_goal_centre.x - 800 * math.copysign(1, enemy_goal_centre.y), enemy_goal_centre.y, 0)
        enemy_goal_right: Vector3 = Vector3(enemy_goal_centre.x + 800 * math.copysign(1, enemy_goal_centre.y), enemy_goal_centre.y, 0)

        ball_to_goal_left: Vector3 = ball_location - enemy_goal_left
        ball_angle_left: float = math.atan2(ball_to_goal_left.y, ball_to_goal_left.x)
        ball_to_goal_right: Vector3 = ball_location - enemy_goal_right
        ball_angle_right: float = math.atan2(ball_to_goal_right.y, ball_to_goal_right.x)
        bot_to_goal_left: Vector3 = bot_location - enemy_goal_left
        bot_angle_left: float = math.atan2(bot_to_goal_left.y, bot_to_goal_left.x)
        bot_to_goal_right: Vector3 = bot_location - enemy_goal_right
        bot_angle_right: float = math.atan2(bot_to_goal_right.y, bot_to_goal_right.x)

        if bot_angle_left > ball_angle_left and bot_angle_right > ball_angle_right:
            # Go to the closest point on the edge of the cone to get a better shot.
            target: Vector3 = calculations.closest_point(enemy_goal_right, ball_location, bot_location)
        elif bot_angle_left < ball_angle_left and bot_angle_right < ball_angle_right:
            # Go to the closest point on the edge of the cone to get a better shot.
            target: Vector3 = calculations.closest_point(enemy_goal_left, ball_location, bot_location)
        else:
            # Hit the ball directly if inside the cone.
            target: Vector3 = bot_location

        self.agent.renderer.draw_rect_3d(enemy_goal_left.to_tuple(), 10, 10, True, self.agent.renderer.blue(), True)
        self.agent.renderer.draw_rect_3d(enemy_goal_right.to_tuple(), 10, 10, True, self.agent.renderer.yellow(), True)
        self.agent.renderer.draw_rect_3d(target.to_tuple(), 10, 10, True, self.agent.renderer.green(), True)
        self.agent.renderer.draw_line_3d(enemy_goal_left.to_tuple(), ball_location.to_tuple(), self.agent.renderer.red())
        self.agent.renderer.draw_line_3d(enemy_goal_right.to_tuple(), ball_location.to_tuple(), self.agent.renderer.red())

        bot_yaw: float = packet.game_cars[self.agent.index].physics.rotation.yaw
        controller: SimpleControllerState = SimpleControllerState()
        controller.steer = steering.gosling_steering(bot_location, bot_yaw, target)  # Sorry Goose
        controller.throttle = 1
        controller.boost = abs(controller.steer) < 0.3

        return controller
