from typing import Optional

from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.ball_prediction_struct import BallPrediction
from rlbot.utils.structures.game_data_struct import GameTickPacket
from RLUtilities.GameInfo import GameInfo
from RLUtilities.LinearAlgebra import vec3
from RLUtilities.Maneuvers import Aerial

from beepboop import BeepBoop
from steps.base_step import BaseStep


class AerialStep(BaseStep):
    def __init__(self, agent: BeepBoop):
        super().__init__(agent)
        self.game_info: GameInfo = GameInfo(agent.index, agent.index)
        self.aerial = Aerial(self.game_info.my_car, vec3(0, 0, 0), 0)
        self.cancellable: bool = False

    def handle_aerial_start(self) -> None:
        ball_prediction: BallPrediction = self.agent.get_ball_prediction_struct()
        # Find the first viable point on the ball path to aerial to
        for i in range(ball_prediction.num_slices):
            loc = ball_prediction.slices[i].physics.location
            self.aerial.target = vec3(loc.x, loc.y, loc.z)
            self.aerial.t_arrival = ball_prediction.slices[i].game_seconds
            if self.aerial.is_viable():
                break

    def get_output(self, packet: GameTickPacket) -> Optional[SimpleControllerState]:
        self.game_info.read_packet(packet)

        # RLUtilities doesn't check for equality properly between equal vec3 objects, so we have to use this ghetto way
        if self.aerial.target[0] == 0 and self.aerial.target[1] == 0 and self.aerial.target[2] == 0:
            self.handle_aerial_start()

        self.aerial.step(1 / 60)

        if not self.aerial.is_viable() or self.aerial.finished:
            self.cancellable = True
            return None
        else:
            return self.aerial.controls
