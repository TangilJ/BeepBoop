from typing import Union

from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from beepboop import BeepBoop
from bot_math.Vector3 import Vector3
from utils import calculations
from pathing.base_path import BasePath
from steps.base_step import BaseStep
from utils.steering import gosling_steering


class PathFollowStep(BaseStep):
    def __init__(self, agent: BeepBoop, path: BasePath):
        super().__init__(agent)
        self.path = path

    def get_output(self, packet: GameTickPacket) -> Union[SimpleControllerState, None]:
        position: Vector3 = Vector3(packet.game_cars[self.agent.index].physics.location)
        yaw: float = packet.game_cars[self.agent.index].physics.rotation.yaw

        while True:
            if len(self.path.path) == 0:
                return None

            if Vector3.distance(position, self.path.path[0]) < 300:
                self.path.remove_points_to_index(0)
            else:
                break

        next_point: Vector3 = self.path.path[0]

        self.path.draw_path()

        steer: float = gosling_steering(position, yaw, next_point)
        handbrake: bool = calculations.angle_to_target(position, yaw, next_point) > 1.75
        boost: bool = calculations.angle_to_target(position, yaw, next_point) < 0.35
        return SimpleControllerState(steer, 1, boost=boost, handbrake=handbrake)
