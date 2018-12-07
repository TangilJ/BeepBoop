from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket


class BeepBoop(BaseAgent):
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        return SimpleControllerState()
