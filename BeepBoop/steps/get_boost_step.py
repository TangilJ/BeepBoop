from typing import Optional, List

from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket, BoostPad, BoostPadState, MAX_BOOSTS

from beepboop import BeepBoop
from bot_math.Vector3 import Vector3
from utils import calculations
from steps.base_step import BaseStep
from utils.steering import gosling_steering


BoostList = BoostPad * MAX_BOOSTS
BoostStateList = BoostPadState * MAX_BOOSTS


class GetBoostStep(BaseStep):
    def __init__(self, agent: BeepBoop):
        super().__init__(agent)
        self.boost_location: Optional[Vector3] = None

    @staticmethod
    def closest_boost(player_pos: Vector3, boost_pads: BoostList, boost_pad_states: BoostStateList) -> Optional[Vector3]:
        closest: Optional[Vector3] = None
        closest_dist: float = float("inf")
        for i in range(len(boost_pads)):
            if boost_pads[i].is_full_boost and boost_pad_states[i].is_active:
                pad: Vector3 = Vector3(boost_pads[i].location)
                current_dist: float = Vector3.distance(player_pos, pad)
                if current_dist < closest_dist:
                    closest_dist = current_dist
                    closest = pad
        return closest

    def get_output(self, packet: GameTickPacket) -> Optional[SimpleControllerState]:
        position: Vector3 = Vector3(packet.game_cars[self.agent.index].physics.location)
        yaw: float = packet.game_cars[self.agent.index].physics.rotation.yaw
        boost_pads: BoostList = self.agent.get_field_info().boost_pads
        boost_pad_states: BoostStateList = packet.game_boosts

        if self.boost_location is None:
            closest: Optional[Vector3] = self.closest_boost(position, boost_pads, boost_pad_states)
            if closest is None:
                return None
            self.boost_location = closest

        steer: float = gosling_steering(position, yaw, self.boost_location)
        handbrake: bool = calculations.angle_to_target(position, yaw, self.boost_location) > 1.75
        boost: bool = calculations.angle_to_target(position, yaw, self.boost_location) < 0.35
        return SimpleControllerState(steer, 1, boost=boost, handbrake=handbrake)
