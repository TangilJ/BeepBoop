import random
from typing import List, Tuple

from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.structures.quick_chats import QuickChats

from beepboop import BeepBoop


_SCORED_ON: List[int] = [QuickChats.Compliments_NiceShot, QuickChats.Compliments_NiceOne, QuickChats.Custom_Compliments_proud,
                         QuickChats.Custom_Compliments_GC, QuickChats.Custom_Compliments_Pro, QuickChats.Reactions_Noooo]
_HAS_SCORED: List[int] = [QuickChats.Reactions_Whew, QuickChats.Compliments_WhatASave, QuickChats.Reactions_Calculated]
_HAS_DEMOED: List[int] = [QuickChats.Apologies_Whoops, QuickChats.Custom_Useful_Demoing]
_GOT_DEMOED: List[int] = [QuickChats.Custom_Toxic_DeAlloc, QuickChats.Apologies_Cursing, QuickChats.Reactions_Wow,
                          QuickChats.Compliments_Thanks]


class QuickChatHandler:
    def __init__(self, agent: BeepBoop) -> None:
        self.agent: BeepBoop = agent
        self.prev_frame_demos: int = 0
        self.prev_frame_score: Tuple[int, int] = (0, 0)

    def handle_quick_chats(self, packet: GameTickPacket) -> None:
        current_score: Tuple[int, int] = QuickChatHandler.get_game_score(packet)

        if current_score[self.agent.team] > self.prev_frame_score[self.agent.team]:
            self.agent.send_quick_chat(QuickChats.CHAT_EVERYONE, random.choice(_HAS_SCORED))
        if current_score[not self.agent.team] > self.prev_frame_score[not self.agent.team]:
            self.agent.send_quick_chat(QuickChats.CHAT_EVERYONE, random.choice(_SCORED_ON))
        if packet.game_cars[self.agent.index].is_demolished:
            self.agent.send_quick_chat(QuickChats.CHAT_EVERYONE, random.choice(_GOT_DEMOED))
        if packet.game_cars[self.agent.index].score_info.demolitions > self.prev_frame_demos:
            self.agent.send_quick_chat(QuickChats.CHAT_EVERYONE, random.choice(_HAS_DEMOED))

        self.prev_frame_demos = packet.game_cars[self.agent.index].score_info.demolitions
        self.prev_frame_score = current_score

    @staticmethod
    def get_game_score(packet: GameTickPacket) -> Tuple[int, int]:
        score: List[int] = [0, 0]  # Index 0 is blue, index 1 is orange

        for car in packet.game_cars:
            score[car.team] += car.score_info.goals

        return score[0], score[1]
