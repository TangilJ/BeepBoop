from rlbot.utils.structures import game_data_struct
from BeepBoop.bot_math.Vector3 import Vector3


class PhysicsObject:
    """Class used as an abstraction layer over `game_data_struct.Physics`.
    Used for objects that have physics components, i.e. cars and the ball.
    It has the same class variables as `game_data_struct.Physics`, but with `Vector3` instead."""

    def __init__(self, physics: game_data_struct.Physics):
        self.location: Vector3 = Vector3(physics.location)
        self.velocity: Vector3 = Vector3(physics.velocity)
        self.rotation: Vector3 = Vector3(physics.rotation)
        self.angular_velocity: Vector3 = Vector3(physics.angular_velocity)
