from rlbot.agents.base_agent import BaseAgent, GameTickPacket, SimpleControllerState
from BeepBoop.steps.base_step import BaseStep
from BeepBoop.steps.kickoff_step import KickoffStep
from BeepBoop.steps.shot_step import ShotStep
from BeepBoop.steps.simple_move_step import SimpleMoveStep
from BeepBoop.bot_math.Vector3 import Vector3
from typing import Optional


class StepHandler:
    def __init__(self, agent: BaseAgent):
        self.agent: BaseAgent = agent
        self.current_step: BaseStep = KickoffStep(self.agent)

    def choose_step(self, packet: GameTickPacket) -> BaseStep:
        ball = Vector3(packet.game_ball.physics.location)
        bot = Vector3(packet.game_cars[self.agent.index].physics.location)

        if ball.x == 0 and ball.y == 0:
            return KickoffStep(self.agent)
        # Go to bot's own goal if the ball is in between the bot and the bot's own goal
        elif (bot.y < ball.y) if self.agent.team else (bot.y > ball.y):
            own_goal: Vector3 = Vector3(self.agent.get_field_info().goals[self.agent.team].location)
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
