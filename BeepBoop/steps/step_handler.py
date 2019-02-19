from typing import Optional

from rlbot.agents.base_agent import GameTickPacket, SimpleControllerState

from beepboop import BeepBoop
from bot_math.Vector3 import Vector3
from steps.base_step import BaseStep
from steps.escape_goal_step import EscapeGoalStep
from steps.kickoff_step import KickoffStep
from steps.save_goal_step import SaveGoalStep
from steps.shot_step import ShotStep
from steps.simple_move_step import SimpleMoveStep
from utils import ball_prediction


class StepHandler:
    def __init__(self, agent: BeepBoop):
        self.agent: BeepBoop = agent
        self.current_step: BaseStep = KickoffStep(self.agent)

    def choose_step(self, packet: GameTickPacket) -> BaseStep:
        ball = Vector3(packet.game_ball.physics.location)
        bot = Vector3(packet.game_cars[self.agent.index].physics.location)
        own_goal: Vector3 = Vector3(self.agent.get_field_info().goals[self.agent.team].location)

        if ball.x == 0 and ball.y == 0:
            return KickoffStep(self.agent)
        elif abs(bot.y) > 5300 and abs(bot.x) < 8000:
            return EscapeGoalStep(self.agent)
        elif ball_prediction.get_ball_in_net(self.agent.get_ball_prediction_struct(), own_goal.y) is not None:
            return SaveGoalStep(self.agent)
        elif (bot.y + 200 < ball.y) if self.agent.team else (bot.y - 200 > ball.y):
            # Go to bot's own goal if the ball is in between the bot and the bot's own goal
            return SimpleMoveStep(self.agent, own_goal)
        else:
            return ShotStep(self.agent)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        out: Optional[SimpleControllerState] = self.current_step.get_output(packet)

        if not self.current_step.cancellable and out is not None:
            return out

        self.current_step = self.choose_step(packet)
        out = self.current_step.get_output(packet)

        if out is not None:
            return out
        else:
            self.agent.logger.warning(f"Agent {self.agent.name} is returning an empty controller on the first frame of the step")
            return SimpleControllerState()
