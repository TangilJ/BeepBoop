from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from BeepBoop.utils.quick_chat_handler import QuickChatHandler


class BeepBoop(BaseAgent):
    def initialize_agent(self) -> None:
        self.quick_chat_handler: QuickChatHandler = QuickChatHandler(self)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.quick_chat_handler.handle_quick_chats(packet)

        return SimpleControllerState()
