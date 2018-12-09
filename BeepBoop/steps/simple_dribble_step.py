from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from .base_step import BaseStep
from BeepBoop.utils.physics_object import PhysicsObject
from BeepBoop.utils import ball_prediction
from BeepBoop.bot_math.Vector3 import Vector3
from RLUtilities.Maneuvers import Drive
from RLUtilities.GameInfo import GameInfo

SPEED_MATCH = 1.3


class SimpleDribbleStep(BaseStep):
    def __init__(self, agent: BaseAgent, arrival_delay: float = 0):
        super().__init__(agent)
        self.arrival_delay: float = arrival_delay
        self.game_info: GameInfo = GameInfo(agent.index, agent.team)

    """Drives towards the ball's first ground bounce and tries to arrive there at the same time as the bounce."""
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.game_info.read_packet(packet)

        bot: PhysicsObject = PhysicsObject(packet.game_cars[self.agent.index].physics)
        bounces = ball_prediction.get_ground_bounces(self.agent.get_ball_prediction_struct())
        if len(bounces) > 0:
            landing, flight_time = bounces[0]
        else:
            # This means that the ball is completely still and will not bounce.
            # Therefore, `landing` is the ball's current position.
            landing, flight_time = Vector3(packet.game_ball.physics.location), packet.game_info.seconds_elapsed

        time_taken: float = flight_time + self.arrival_delay - packet.game_info.seconds_elapsed
        to_target: Vector3 = landing - bot.location
        distance: float = to_target.magnitude()
        average_speed: float = distance / (time_taken + 0.0000001)
        current_speed: float = bot.velocity.magnitude()
        target_speed: float = (1 - SPEED_MATCH) * current_speed + SPEED_MATCH * average_speed

        drive: Drive = Drive(self.game_info.my_car, landing.to_rlutilities_vec3(), target_speed)
        drive.step(0.01666)

        return drive.controls
