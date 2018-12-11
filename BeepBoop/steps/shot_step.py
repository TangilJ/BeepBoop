from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from BeepBoop.steps.base_step import BaseStep
from BeepBoop.utils import steering
from BeepBoop.utils import calculations
from BeepBoop.bot_math.Vector3 import Vector3
import math


class ShotStep(BaseStep):
    def __init__(self, agent: BaseAgent):
        super().__init__(agent)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # ShotStep is a port of Gosling's calcShot.
        # See RLBot Start-To-Finish episode 5 (https://youtu.be/GPjrWW9zcRQ) for a good explanation of what this code does.
        # I thoroughly apologise for all this code. It is a mess.

        bot_location: Vector3 = Vector3(packet.game_cars[self.agent.index].physics.location)
        ball_velocity: Vector3 = Vector3(packet.game_ball.physics.velocity)
        ball_location: Vector3 = Vector3(packet.game_ball.physics.location)

        enemy_goal_centre: Vector3 = Vector3(self.agent.get_field_info().goals[not self.agent.team].location)
        enemy_goal_left: Vector3 = Vector3(enemy_goal_centre.x - 800 * math.copysign(1, enemy_goal_centre.y), enemy_goal_centre.y,
                                           0)
        enemy_goal_right: Vector3 = Vector3(enemy_goal_centre.x + 800 * math.copysign(1, enemy_goal_centre.y),
                                            enemy_goal_centre.y, 0)

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
            target: Vector3 = enemy_goal_right
        elif bot_angle_left < ball_angle_left and bot_angle_right < ball_angle_right:
            # Go to the closest point on the edge of the cone to get a better shot.
            target: Vector3 = enemy_goal_left
        else:
            # Hit the ball directly if inside the cone.
            target: Vector3 = None

        if target is not None:
            goal_to_ball: Vector3 = (ball_location - target).normalised()
            goal_to_bot: Vector3 = (bot_location - target).normalised()
            difference: Vector3 = goal_to_ball - goal_to_bot
            error = min(max(abs(difference.x) + abs(difference.y), 1), 10)
        else:
            goal_to_ball: Vector3 = (bot_location - ball_location).normalised()
            error = min(max(Vector3.distance(ball_location, bot_location), 0), 1)

        dpp: float = (((ball_location.x - bot_location.x) * ball_velocity.x) + (
                (ball_location.y - bot_location.y) * ball_velocity.y)) / Vector3.distance(ball_location, bot_location)
        ball_dpp_skew: float = min(max(abs(dpp), 1), 1.5)

        target_distance: float = min(max((40 + Vector3.distance(ball_location, bot_location) * error ** 2) / 1.8, 0), 4000)
        target_location: Vector3 = Vector3(goal_to_ball.x * ball_dpp_skew, goal_to_ball.y, 0) * target_distance + ball_location
        ball_something: float = ((((target_location.x - target_location.x) * ball_velocity.x) + (
                (target_location.y - bot_location.y) * ball_velocity.y)) / Vector3.distance(ball_location, bot_location)) ** 2

        if ball_something > 100:
            ball_something = min(max(ball_something, 0), 80)
            correction: Vector3 = ball_velocity.normalised()
            correction *= ball_something
            target_location += correction

        extra: float = 4120 - abs(target_location.x)
        if extra < 0:
            target_location.x = min(max(target_location.x, -4120), 4120)
            target_location.y = target_location.y - math.copysign(1, self.agent.team) * min(max(extra, -500), 500)

        self.agent.renderer.draw_rect_3d(enemy_goal_left.to_tuple(), 10, 10, True, self.agent.renderer.blue(), True)
        self.agent.renderer.draw_rect_3d(enemy_goal_right.to_tuple(), 10, 10, True, self.agent.renderer.yellow(), True)
        self.agent.renderer.draw_rect_3d(target_location.to_tuple(), 10, 10, True, self.agent.renderer.green(), True)
        self.agent.renderer.draw_line_3d(enemy_goal_left.to_tuple(), ball_location.to_tuple(), self.agent.renderer.red())
        self.agent.renderer.draw_line_3d(enemy_goal_right.to_tuple(), ball_location.to_tuple(), self.agent.renderer.red())

        bot_yaw: float = packet.game_cars[self.agent.index].physics.rotation.yaw
        controller: SimpleControllerState = SimpleControllerState()
        controller.steer = steering.gosling_steering(bot_location, bot_yaw, target_location)  # Sorry Goose
        controller.throttle = 1
        controller.boost = abs(controller.steer) < 0.3
        controller.handbrake = abs(calculations.angle_to_target(bot_location, bot_yaw, target_location)) > 1.8

        return controller
