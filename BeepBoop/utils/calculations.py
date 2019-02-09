import math

from bot_math.Vector3 import Vector3


def closest_point(p1: Vector3, p2: Vector3, p3: Vector3) -> Vector3:
    """
    Determines the point closest to p3 on the line p1p2.

    :param p1: Starting point of the line
    :param p2: Ending point of the line
    :param p3: Point outside the line
    :return: Point closest to p3 on the line p1p2
    """
    k = ((p2.y - p1.y) * (p3.x - p1.x) - (p2.x - p1.x) * (p3.y - p1.y)) / ((p2.y - p1.y) ** 2 + (p2.x - p1.x) ** 2)
    x4 = p3.x - k * (p2.y - p1.y)
    y4 = p3.y + k * (p2.x - p1.x)

    return Vector3(x4, y4, 0)


def angle_to_target(position: Vector3, yaw: float, target: Vector3) -> float:
    """
    Determines the angle (in radians) from the front of the car to the ``target``.

    :param position: Position of the car
    :param yaw: Yaw of the car
    :param target: Position of what to get the angle to
    :return: Angle from the front of the car to the target
    """
    angle_between_bot_and_target = math.atan2(target.y - position.y,
                                              target.x - position.x)

    angle_front_to_target = angle_between_bot_and_target - yaw

    # Correct the values
    if angle_front_to_target < -math.pi:
        angle_front_to_target += 2 * math.pi
    if angle_front_to_target > math.pi:
        angle_front_to_target -= 2 * math.pi

    return angle_front_to_target


def sign(n: float) -> int:
    """
    Determines the sign of ``n``.

    :param n: Number to check the sign of
    :return: Returns if 1 if n is positive, else returns -1
    """
    return 1 if n > 0 else -1
