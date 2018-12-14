# Code was ported hastily from an old BeepBoop version so the code is going to be quite bad.

from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.ball_prediction_struct import Slice
from .base_step import BaseStep
from BeepBoop.utils import ball_prediction
from BeepBoop.bot_math.Vector3 import Vector3
from RLUtilities.GameInfo import GameInfo
import math

SPEED_MATCH = 1.3


class SimpleDribbleStep(BaseStep):
    def __init__(self, agent: BaseAgent, arrival_delay: float = 0):
        super().__init__(agent)
        self.arrival_delay: float = arrival_delay
        self.game_info: GameInfo = GameInfo(agent.index, agent.team)
        self.controller: SimpleControllerState = SimpleControllerState()
        self.bot_vel: Vector3 = Vector3(0, 0, 0)
        self.bot_yaw: float = 0
        self.bot_pos: Vector3 = Vector3(0, 0, 0)

    def arrive_on_time(self, target: Vector3, time_taken: float):
        to_target = target - self.bot_pos
        distance = to_target.magnitude()
        average_speed = distance / time_taken
        current_speed = self.bot_vel.magnitude()
        target_speed = (1 - SPEED_MATCH) * current_speed + SPEED_MATCH * average_speed

        if current_speed < target_speed:
            self.controller.throttle = 1
            self.controller.boost = target_speed > 1410
        else:
            self.controller.boost = False
            if current_speed - target_speed > 75:
                self.controller.throttle = -1
            else:
                self.controller.throttle = 0

        if current_speed < 100:
            self.controller.throttle = 0.2

    def angle_to_target(self, target):
        angle_between_bot_and_target = math.degrees(math.atan2(target.y - self.bot_pos.y,
                                                               target.x - self.bot_pos.x))

        angle_front_to_target = angle_between_bot_and_target - self.bot_yaw

        # Correct the values
        if angle_front_to_target < -180:
            angle_front_to_target += 360
        if angle_front_to_target > 180:
            angle_front_to_target -= 360

        return angle_front_to_target

    def aim(self, angle):
        if angle < -10:
            # If the target is more than 10 degrees right from the centre, steer left
            self.controller.steer = -1
        elif angle > 10:
            # If the target is more than 10 degrees left from the centre, steer right
            self.controller.steer = 1
        else:
            # If the target is less than 10 degrees from the centre, steer straight
            self.controller.steer = 0

        self.controller.handbrake = abs(angle) > 105

    """Drives towards the ball's first ground bounce and tries to arrive there at the same time as the bounce."""

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        bot_rot = Vector3(packet.game_cars[self.agent.index].physics.rotation)
        self.bot_yaw = math.degrees(bot_rot.z)
        self.bot_vel = Vector3(packet.game_cars[self.agent.index].physics.velocity)
        self.bot_pos = Vector3(packet.game_cars[self.agent.index].physics.location)
        self.game_info.read_packet(packet)

        bounce: Slice = ball_prediction.get_ground_bounces(self.agent.get_ball_prediction_struct()[0])
        self.arrive_on_time(Vector3(bounce.physics.location), bounce.game_seconds - packet.game_info.seconds_elapsed)
        self.aim(self.angle_to_target(Vector3(bounce.physics.location)))

        return self.controller
