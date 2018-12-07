from bot_math.Vector3 import Vector3
import math


def simple_aim(position: Vector3, yaw: float, target: Vector3) -> float:
    pos_to_target = target - position
    facing = Vector3(math.cos(yaw), math.sin(yaw), 0)
    self_right = Vector3.cross_product(facing, Vector3(0, 0, 1))

    if Vector3.dot_product(self_right, pos_to_target) < 0:
        return 1.0
    else:
        return -1.0
