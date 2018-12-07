from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from BeepBoop.steps.base_step import BaseStep
from BeepBoop.utils.physics_object import PhysicsObject
from BeepBoop.utils import steering
from BeepBoop.bot_math.Vector3 import Vector3


class SimpleMoveStep(BaseStep):
    def __init__(self, agent: BaseAgent, target: Vector3):
        super().__init__(agent)
        self.target: Vector3 = target

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        bot: PhysicsObject = PhysicsObject(packet.game_cars[self.agent.index].physics)
        steer: float = steering.simple_aim(bot.location, bot.rotation.z, self.target)

        controller: SimpleControllerState = SimpleControllerState()
        controller.steer = steer
        controller.throttle = 1

        return controller
