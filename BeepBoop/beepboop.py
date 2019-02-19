import sys
import os
path = os.path.dirname(__file__)
sys.path.append(path)

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from RLUtilities.GameInfo import GameInfo


class BeepBoop(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)

        from steps.step_handler import StepHandler
        from utils.quick_chat_handler import QuickChatHandler

        self.quick_chat_handler: QuickChatHandler = QuickChatHandler(self)
        self.step_handler: StepHandler = StepHandler(self)
        self.game_info: GameInfo = GameInfo(self.index, self.team)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.game_info.read_packet(packet)
        self.quick_chat_handler.handle_quick_chats(packet)

        self.renderer.begin_rendering()
        output: SimpleControllerState = self.step_handler.get_output(packet)

        step_name: str = type(self.step_handler.current_step).__name__
        text_pos_y: float = 15 + 15 * self.index
        self.renderer.draw_string_2d(10, text_pos_y, 1, 1, f"Step: {step_name}", self.renderer.cyan())

        self.renderer.end_rendering()

        return output
