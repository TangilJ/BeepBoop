from abc import ABCMeta, abstractmethod
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from typing import Union


class BaseStep(metaclass=ABCMeta):
    def __init__(self, agent: BaseAgent):
        self.agent: BaseAgent = agent

        self.cancellable: bool = True

    @abstractmethod
    def get_output(self, packet: GameTickPacket) -> Union[SimpleControllerState, None]:
        pass
