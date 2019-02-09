from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.base_agent import SimpleControllerState

from beepboop import BeepBoop
from bot_math.Vector3 import Vector3
from steps.base_step import BaseStep
from utils import steering
from utils.physics_object import PhysicsObject


class SimpleMoveStep(BaseStep):
    def __init__(self, agent: BeepBoop, target: Vector3):
        super().__init__(agent)
        self.target: Vector3 = target

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        bot: PhysicsObject = PhysicsObject(packet.game_cars[self.agent.index].physics)
        steer: float = steering.gosling_steering(bot.location, bot.rotation.z, self.target)

        controller: SimpleControllerState = SimpleControllerState()
        controller.steer = steer
        controller.throttle = 1

        return controller
