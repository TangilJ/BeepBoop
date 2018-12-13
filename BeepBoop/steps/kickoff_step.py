from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.base_agent import SimpleControllerState, BaseAgent
from BeepBoop.steps.base_step import BaseStep
from BeepBoop.bot_math.Vector3 import Vector3
from typing import List, Optional, Union
from RLUtilities.Maneuvers import AirDodge, Drive, DoNothing
from RLUtilities.GameInfo import GameInfo
from RLUtilities.LinearAlgebra import vec3, normalize

KICKOFF_ACTION = Union[AirDodge, Drive, DoNothing]


class KickoffStep(BaseStep):

    def __init__(self, agent: BaseAgent):
        super().__init__(agent)
        self.cancellable: bool = False
        self.kickoff_steps: Optional[List[KICKOFF_ACTION]] = None
        self.game_info: GameInfo = GameInfo(agent.index, agent.team)

    def prepare_kickoff(self, packet: GameTickPacket) -> None:
        bot = Vector3(packet.game_cars[self.agent.index].physics.location)

        # DoNothing is put before AirDodge because we don't want the bot to boost when it's dodging,
        # and so we reset the controller first
        if abs(bot.x) < 250:
            # Centre kickoff
            self.kickoff_steps = [
                Drive(self.game_info.my_car, vec3(0, 3500 * (1 if self.agent.team else -1), 0), 2400),
                DoNothing(),
                AirDodge(self.game_info.my_car, 0.1, vec3(0, 0, 0)),
                Drive(self.game_info.my_car, vec3(0, 300 * (1 if self.agent.team else -1), 0), 2400),
                DoNothing(),
                AirDodge(self.game_info.my_car, 0.1, vec3(0, 0, 0)),
            ]
        elif abs(bot.x) < 1000:
            # Off-centre kickoff
            self.kickoff_steps = [
                Drive(self.game_info.my_car, vec3(0, 2700 * (1 if self.agent.team else -1), 0), 2400),
                Drive(self.game_info.my_car, vec3(0, 1000 * (1 if self.agent.team else -1), 0), 2400),
                DoNothing(),
                AirDodge(self.game_info.my_car, 0.1, vec3(0, 0, 0)),
                Drive(self.game_info.my_car, vec3(0, 300 * (1 if self.agent.team else -1), 0), 2400),
                DoNothing(),
                AirDodge(self.game_info.my_car, 0.1, vec3(0, 0, 0)),
            ]
        else:
            spawn_to_ball_norm: vec3 = normalize(self.game_info.my_car.pos)
            # Diagonal kickoff
            self.kickoff_steps = [
                Drive(self.game_info.my_car, vec3(0, 0, 0) + spawn_to_ball_norm * 200, 2400),
                DoNothing(),
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
                if isinstance(step, DoNothing):
                    self.kickoff_steps.pop(0)
                    step = self.kickoff_steps[0]
                    return step.controls

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
            step.step(1 / 60)
            return step.controls
        else:
            self.cancellable = True
            self.agent.logger.warning(f"Agent {self.agent.name}: Uh oh. Ran out of steps in kickoff.")
            return None
