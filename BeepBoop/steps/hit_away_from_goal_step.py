from typing import Optional

from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from RLUtilities.GameInfo import GameInfo
from RLUtilities.LinearAlgebra import vec3
from RLUtilities.Maneuvers import AirDodge

from beepboop import BeepBoop
from bot_math.Vector3 import Vector3
from steps.base_step import BaseStep
from utils.physics_object import PhysicsObject
from utils.steering import gosling_steering


class HitAwayFromGoalStep(BaseStep):
    def __init__(self, agent: BeepBoop):
        super().__init__(agent)
        self.game_info: GameInfo = GameInfo(agent.index, agent.index)
        self.dodge: Optional[AirDodge] = None

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # Hit the ball blindly if the bot is between the ball and its own goal. This is to clear it away.
        # Hit the ball to the side if the ball is closer to its own goal than it is.

        self.game_info.read_packet(packet)

        if self.dodge is not None:
            self.dodge.step(1 / 60)
            if not self.dodge.finished:
                return self.dodge.controls
            else:
                self.dodge = None

        controller: SimpleControllerState = SimpleControllerState()

        ball: Vector3 = Vector3(packet.game_ball.physics.location)
        bot: PhysicsObject = PhysicsObject(packet.game_cars[self.agent.index].physics)

        target: Vector3
        if abs(ball.y) < abs(bot.location.y):
            target = ball
        else:
            offset: float = 100 if ball.x > bot.location.x else -100
            offset *= -1 if self.agent.team == 1 else 1
            target = ball + Vector3(offset, 0, 0)
            bot_to_ball: Vector3 = ball - bot.location
            if abs(bot_to_ball.normalised().x) > 0.7:
                self.dodge = AirDodge(self.game_info.my_car, 0.1, vec3(ball.x, ball.y, ball.z))

        controller.steer = gosling_steering(bot.location, bot.rotation.z, target)
        controller.boost = True
        controller.throttle = 1

        return controller
