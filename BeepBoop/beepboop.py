from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from BeepBoop.utils.quick_chat_handler import QuickChatHandler
from BeepBoop.steps.step_handler import StepHandler


class BeepBoop(BaseAgent):
    def initialize_agent(self) -> None:
        self.quick_chat_handler: QuickChatHandler = QuickChatHandler(self)
        self.step_handler: StepHandler = StepHandler(self)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.quick_chat_handler.handle_quick_chats(packet)

        return self.step_handler.get_output(packet)
