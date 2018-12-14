from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from BeepBoop.steps.base_step import BaseStep


class HitAwayFromGoalStep(BaseStep):
    def __init__(self, agent: BaseAgent):
        super().__init__(agent)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        controller: SimpleControllerState = SimpleControllerState()
        controller.throttle = 1

        return controller
