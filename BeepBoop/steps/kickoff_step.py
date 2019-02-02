from typing import List, Optional, Union

from rlbot.agents.base_agent import SimpleControllerState, BaseAgent
from rlbot.utils.structures.game_data_struct import GameTickPacket, BoostPad
from RLUtilities.GameInfo import GameInfo
from RLUtilities.LinearAlgebra import vec3, normalize
from RLUtilities.Maneuvers import AirDodge, Drive

from bot_math.Vector3 import Vector3
from steps.base_step import BaseStep


KICKOFF_ACTION = Union[AirDodge, Drive]


class KickoffStep(BaseStep):

    def __init__(self, agent: BaseAgent):
        super().__init__(agent)
        self.cancellable: bool = False
        self.kickoff_steps: Optional[List[KICKOFF_ACTION]] = None
        self.game_info: GameInfo = GameInfo(agent.index, agent.team)

    def get_closest_small_pad(self, bot_pos: Vector3) -> BoostPad:
        closest_pad: BoostPad = None
        dist_to_closest_pad: float = float("inf")

        for boost_pad in self.agent.get_field_info().boost_pads:
            current_pad: BoostPad = boost_pad
            current_pos: Vector3 = Vector3(current_pad.location)
            dist_to_current_pad = Vector3.distance(bot_pos, current_pos)

            if not current_pad.is_full_boost and dist_to_current_pad < dist_to_closest_pad:
                dist_to_closest_pad = dist_to_current_pad
                closest_pad = current_pad

        return closest_pad

    def prepare_kickoff(self, packet: GameTickPacket) -> None:
        bot_pos = Vector3(packet.game_cars[self.agent.index].physics.location)

        # Centre kickoff
        if abs(bot_pos.x) < 250:
            pad = self.get_closest_small_pad(bot_pos).location
            first_target: vec3 = vec3(pad.x, pad.y, pad.z) - vec3(0, 250, 0) * (1 if self.agent.team else -1)
            second_target: vec3 = vec3(0, 850, 0) * (1 if self.agent.team else -1)

            self.kickoff_steps = [
                Drive(self.game_info.my_car, first_target, 2400),
                AirDodge(self.game_info.my_car, 0.075, vec3(0, 0, 0)),
                Drive(self.game_info.my_car, second_target, 2400),
                AirDodge(self.game_info.my_car, 0.075, vec3(0, 0, 0))
            ]
        # Off-centre kickoff
        elif abs(bot_pos.x) < 1000:
            target: vec3 = normalize(self.game_info.my_car.pos) * 500

            self.kickoff_steps = [
                Drive(self.game_info.my_car, vec3(self.game_info.my_car.pos[0], 3477 * (1 if self.agent.team else -1), 0), 2400),
                AirDodge(self.game_info.my_car, 0.075, vec3(0, 0, 0)),
                Drive(self.game_info.my_car, target, 2400),
                AirDodge(self.game_info.my_car, 0.075, vec3(0, 0, 0))
            ]
        # Diagonal kickoff
        else:
            pad = self.get_closest_small_pad(bot_pos).location
            car_to_pad: vec3 = vec3(pad.x, pad.y, pad.z) - self.game_info.my_car.pos
            first_target: vec3 = self.game_info.my_car.pos + 1.425 * car_to_pad
            second_target: vec3 = vec3(0, 150, 0) * (1 if self.agent.team else -1)
            third_target: vec3 = normalize(self.game_info.my_car.pos) * 850

            self.kickoff_steps = [
                Drive(self.game_info.my_car, first_target, 2300),
                AirDodge(self.game_info.my_car, 0.035, second_target),
                Drive(self.game_info.my_car, third_target, 2400),
                AirDodge(self.game_info.my_car, 0.1, vec3(0, 0, 0))
            ]

    def get_output(self, packet: GameTickPacket) -> Optional[SimpleControllerState]:
        self.game_info.read_packet(packet)

        ball = packet.game_ball.physics.location
        if ball.x != 0 or ball.y != 0:
            return None

        if self.kickoff_steps is None:
            self.prepare_kickoff(packet)

        if len(self.kickoff_steps) > 0:
            step: KICKOFF_ACTION = self.kickoff_steps[0]
            while step.finished:
                if len(self.kickoff_steps) == 0:
                    self.cancellable = True
                    self.agent.logger.warning(f"Agent {self.agent.name}: Uh oh. Ran out of steps in kickoff.")
                    return None

                self.kickoff_steps.pop(0)

                # TODO: Fix this spaghetti-ass duplicate code
                if len(self.kickoff_steps) == 0:
                    self.cancellable = True
                    self.agent.logger.warning(f"Agent {self.agent.name}: Uh oh. Ran out of steps in kickoff.")
                    return None

                step = self.kickoff_steps[0]

            if isinstance(step, Drive) and not self.game_info.my_car.on_ground:
                # Do not do anything until the car gets on the ground
                return SimpleControllerState()

            step.step(1 / 60)
            return step.controls
        else:
            self.cancellable = True
            self.agent.logger.warning(f"Agent {self.agent.name}: Uh oh. Ran out of steps in kickoff.")
            return None
