from typing import List

from bot_math.Vector3 import Vector3


HALF_GOAL_WIDTH: float = 892.755
GOAL_LINE_Y: int = 5120


def in_shooting_cone(car: Vector3, ball: Vector3, goal_y_sign: float) -> bool:
    """
    Determines whether the car is in the shooting cone.

    :param car: Position of the car
    :param ball: Position of the ball
    :param goal_y_sign: Sign of the Y position of the goal the car is shooting at
    :return: True if the car is in the shooting cone. False if it is not.
    """
    car_to_ball: Vector3 = ball - car
    normalised: Vector3 = car_to_ball.normalised()
    dist_y_ball_to_goal: float = goal_y_sign * GOAL_LINE_Y - ball.y
    multiplies_to_goal_y: float = dist_y_ball_to_goal / normalised.y
    pos_x_ball_in_goal = ball.x + multiplies_to_goal_y * normalised

    if abs(pos_x_ball_in_goal) < HALF_GOAL_WIDTH:
        return True
    return False


def linear_bezier(p0: Vector3, p1: Vector3, points: int = 20) -> List[Vector3]:
    """
    Generates a linear bezier curve from points p0 and p1.
    Each point is equally spaced in terms of interpolation value.

    :param p0: Starting point
    :param p1: Ending point
    :param points: Number of points to include in the point list
    :return: Generated path as a list of points
    """

    path: List[Vector3] = []

    interval: float = 1 / points
    for point_num in range(0, points):
        t = point_num * interval
        point = (1 - t) * p0 + t * p1
        path.append(point)

    return path


def quadratic_bezier(p0: Vector3, p1: Vector3, p2: Vector3, points: int = 20) -> List[Vector3]:
    """
    Generates a quadratic bezier curve from points p0, p1, and p2.
    Each point is equally spaced in terms of interpolation value.

    :param p0: Starting point
    :param p1: Intermediate point
    :param p2: Ending point
    :param points: Number of points to include in the point list
    :return: Generated path as a list of points
    """
    path: List[Vector3] = []

    interval: float = 1 / points
    for point_num in range(0, points):
        t = point_num * interval
        point = p1 + (1 - t) ** 2 * (p0 - p1) + t ** 2 * (p2 - p1)
        path.append(point)

    return path


def cubic_bezier(p0: Vector3, p1: Vector3, p2: Vector3, p3: Vector3, points: int = 20) -> List[Vector3]:
    """
    Generates a cubic bezier curve from points p0, p1, p2, and p3.
    Each point is equally spaced in terms of interpolation value.

    :param p0: Starting point
    :param p1: First intermediate point
    :param p2: Second intermediate point
    :param p3: Ending point
    :param points: Number of points to include in the point list
    :return: Generated path as a list of points
    """
    path: List[Vector3] = []

    interval: float = 1 / points
    for point_num in range(0, points):
        t = point_num * interval
        point = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3
        path.append(point)

    return path
