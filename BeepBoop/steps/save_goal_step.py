from typing import Optional, List, Union

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.ball_prediction_struct import Slice, BallPrediction
from rlbot.utils.structures.game_data_struct import GameTickPacket
from RLUtilities.Maneuvers import Aerial
from RLUtilities.GameInfo import GameInfo

from bot_math.Vector3 import Vector3
from steps.aerial_step import AerialStep
from steps.base_step import BaseStep
from steps.hit_away_from_goal_step import HitAwayFromGoalStep
from steps.simple_dribble_step import SimpleDribbleStep
from utils.ball_prediction import get_ball_in_net, get_ground_bounces


MIN_Z_VEL = 400  # used to see if the ball comes from a high enough height to get underneath it


class SaveGoalStep(BaseStep):
    def __init__(self, agent: BaseAgent):
        super().__init__(agent)
        self.cancellable: bool = False
        self.aerial: Optional[Aerial] = None
        self.game_info: GameInfo = GameInfo(agent.index, agent.team)
        self.current_action: Optional[Union[AerialStep, SimpleDribbleStep, HitAwayFromGoalStep]] = None

    @staticmethod
    def bounces_filter(bounces: List[Slice], ball_net_time: float, minimum_z_vel: float) -> List[Slice]:
        """Gets all bounces that have at least the minimum z velocity and are before it reaches the net."""
        # Using this method instead of filter with lambda to get slightly more performance
        filtered: List[Slice] = []
        for bounce in bounces:
            if bounce.game_seconds > ball_net_time:
                break
            if abs(bounce.physics.velocity.z) > minimum_z_vel:
                filtered.append(bounce)

        return filtered

    @staticmethod
    def closest_point(points: List[Slice], position: Vector3) -> Optional[Slice]:
        closest: Optional[Slice] = None
        closest_dist: float = float("inf")
        for point in points:
            dist = Vector3.distance(position, Vector3(point.physics.location))
            if dist < closest_dist:
                closest = point
                closest_dist = dist

        return closest

    def get_output(self, packet: GameTickPacket) -> Optional[SimpleControllerState]:
        goal: Vector3 = Vector3(self.agent.get_field_info().goals[self.agent.team].location)
        ball_prediction: BallPrediction = self.agent.get_ball_prediction_struct()
        ball_in_net: Optional[Slice] = get_ball_in_net(ball_prediction, goal.y)
        if ball_in_net is None:
            self.cancellable = True
            return None

        self.game_info.read_packet(packet)

        if self.current_action is None:
            # Figure out what action to take (aerial, dribble, or kicking the ball away)
            ground_bounces: List[Slice] = get_ground_bounces(self.agent.get_ball_prediction_struct())
            ground_bounces_filtered: List[Slice] = self.bounces_filter(ground_bounces, ball_in_net.game_seconds, MIN_Z_VEL)

            if len(ground_bounces_filtered) > 0:
                self.current_action = SimpleDribbleStep(self.agent)
            else:
                self.current_action = HitAwayFromGoalStep(self.agent)

        return self.current_action.get_output(packet)
