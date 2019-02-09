from abc import ABCMeta, abstractmethod
from typing import Union

from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.base_agent import SimpleControllerState

from beepboop import BeepBoop


class BaseStep(metaclass=ABCMeta):
    def __init__(self, agent: BeepBoop):
        self.agent: BeepBoop = agent

        self.cancellable: bool = True

    @abstractmethod
    def get_output(self, packet: GameTickPacket) -> Union[SimpleControllerState, None]:
        pass
