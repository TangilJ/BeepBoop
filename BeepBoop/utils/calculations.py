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


def line_line_intersection(a1: Vector3, a2: Vector3, b1: Vector3, b2: Vector3) -> Vector3:
    """
    Determines the intersection point of line a1a2 and line b1b2.
    Both lines are assumed to be infinitely long.

    :param a1: Starting point of line 1
    :param a2: Ending point of line 1
    :param b1: Starting point of line 2
    :param b2: Ending point of line 2
    :return: The intersection point of line 1 and line 2
    """
    # From https://stackoverflow.com/a/20677983/7245441

    def det(a: Vector3, b: Vector3) -> float:
        return a.x * b.y - a.y * b.x

    y_diff = Vector3(a1.y - a2.y, b1.y - b2.y, 0)
    x_diff = Vector3(a1.x - a2.x, b1.x - b2.x, 0)

    div = det(x_diff, y_diff)
    if div == 0:
        raise Exception("Lines do not intersect")

    d = Vector3(det(a1, a2), det(b1, b2), 0)
    x = det(d, x_diff) / div
    y = det(d, y_diff) / div

    return Vector3(x, y, 0)
