from BeepBoop.bot_math.Vector3 import Vector3
from BeepBoop.utils import calculations
import math


def simple_aim(position: Vector3, yaw: float, target: Vector3) -> float:
    """Bang bang controller for steering."""
    pos_to_target: Vector3 = target - position
    facing: Vector3 = Vector3(math.cos(yaw), math.sin(yaw), 0)
    self_right: Vector3 = Vector3.cross_product(facing, Vector3(0, 0, 1))

    if Vector3.dot_product(self_right, pos_to_target) < 0:
        return 1.0
    else:
        return -1.0


def gosling_steering(position: Vector3, yaw: float, target: Vector3) -> float:
    """Simple steering used in Gosling"""
    # Absolutely shamelessly stealing this from Gosling (sorry Goose)
    # https://github.com/ddthj/Gosling/blob/master/Episode%205%20Code/Util.py#L128
    angle_to_ball: float = calculations.angle_to_target(position, yaw, target)
    steer_value: float = ((10 * angle_to_ball + math.copysign(1, angle_to_ball)) ** 3) / 20

    return steer_value
