from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from beepboop import BeepBoop
from pathing.shooting_path import ShootingPath
from steps.base_step import BaseStep
from steps.path_follow_step import PathFollowStep


class ShotStep(BaseStep):
    def __init__(self, agent: BeepBoop):
        super().__init__(agent)
        self.path: ShootingPath = ShootingPath(agent)
        self.follow = PathFollowStep(agent, self.path)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # TODO: If the car is far enough away from all points or is facing the wrong direction, redraw the curve
        # ^ E.g. the angle between its direction and the direction between 2 consequent points is too large

        if self.path.path is []:
            self.path.generate_path(packet)

        return self.follow.get_output(packet)
