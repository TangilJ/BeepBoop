from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from BeepBoop.steps.base_step import BaseStep
from BeepBoop.utils.ball_prediction import get_ball_in_net
from BeepBoop.bot_math.Vector3 import Vector3
from typing import Optional, Tuple


class SaveGoalStep(BaseStep):
    def __init__(self, agent: BaseAgent):
        super().__init__(agent)
        self.cancellable = False

    def get_output(self, packet: GameTickPacket) -> Optional[SimpleControllerState]:
        goal: Vector3 = Vector3(self.agent.get_field_info().goals[self.agent.team].location)
        ball_location_in_net: Optional[Tuple[Vector3, float]] = get_ball_in_net(self.agent.get_ball_prediction_struct(), goal.y)

        if ball_location_in_net is None:
            self.cancellable = True
            return None

        return SimpleControllerState()
