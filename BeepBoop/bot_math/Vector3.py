import math
from typing import Tuple, Optional, Union

import rlbot.utils.structures.game_data_struct as game_data_struct
from RLUtilities.LinearAlgebra import vec3


Number = Union[int, float]
VectorArgument = Union[Number, game_data_struct.Vector3, game_data_struct.Rotator, vec3]


class Vector3:
    def __init__(self, x: VectorArgument, y: Optional[Number] = None, z: Optional[Number] = None):
        self.x: Number = 0
        self.y: Number = 0
        self.z: Number = 0

        if isinstance(x, game_data_struct.Vector3):
            self.x = x.x
            self.y = x.y
            self.z = x.z
        elif isinstance(x, game_data_struct.Rotator):
            self.x = x.roll
            self.y = x.pitch
            self.z = x.yaw
        elif isinstance(x, vec3):
            self.x = x[0]
            self.y = x[1]
            self.z = x[2]
        elif y is not None and z is not None:
                self.x = x
                self.y = y
                self.z = z
        else:
            raise TypeError("Wrong type(s) given for Vector3.y and/or Vector3.z")

    def __add__(self, v: "Vector3") -> "Vector3":
        return Vector3(self.x + v.x, self.y + v.y, self.z + v.z)

    def __sub__(self, v: "Vector3") -> "Vector3":
        return Vector3(self.x - v.x, self.y - v.y, self.z - v.z)

    def __mul__(self, v: Number) -> "Vector3":
        return Vector3(self.x * v, self.y * v, self.z * v)

    def __truediv__(self, v: Number) -> "Vector3":
        return Vector3(self.x / v, self.y / v, self.z / v)

    def __rmul__(self, v: Number) -> "Vector3":
        return Vector3(self.x * v, self.y * v, self.z * v)

    def __rtruediv__(self, v: Number) -> "Vector3":
        return Vector3(self.x / v, self.y / v, self.z / v)

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: "Vector3") -> bool:
        if isinstance(other, Vector3):
            if other.x == self.y and other.y == self.y and other.z == self.z:
                return True
            return False
        return False

    def __getitem__(self, item: int) -> Number:
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z
        else:
            raise IndexError("Invalid index for accessing Vector3. Must be 0, 1, or 2.")

    def __setitem__(self, key: int, value: Number):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            raise IndexError("Invalid index for accessing Vector3. Must be 0, 1, or 2.")

    def magnitude(self) -> Number:
        return abs(math.sqrt(self.x**2 + self.y**2 + self.z**2))

    def normalised(self) -> "Vector3":
        mag = self.magnitude()
        return Vector3(self.x / mag, self.y / mag, self.z / mag)

    def to_rlutilities_vec3(self) -> vec3:
        return vec3(self.x, self.y, self.z)

    def to_tuple(self) -> Tuple[Number, Number, Number]:
        return self.x, self.y, self.z

    @staticmethod
    def dot_product(v1: "Vector3", v2: "Vector3") -> Number:
        return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z

    @staticmethod
    def cross_product(v1: "Vector3", v2: "Vector3") -> "Vector3":
        x = v1.y * v2.z - v1.z * v2.y
        y = v1.z * v2.x - v1.x * v2.z
        z = v1.x * v2.y - v1.y * v2.x
        return Vector3(x, y, z)

    @staticmethod
    def reflect(vector: "Vector3", normal: "Vector3") -> "Vector3":
        dot = Vector3.dot_product(vector, normal)
        return Vector3(vector.x - 2 * dot * normal.x,
                       vector.y - 2 * dot * normal.y,
                       vector.z - 2 * dot * normal.z)

    @staticmethod
    def distance(p1: "Vector3", p2: "Vector3") -> Number:
        return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)

    @staticmethod
    def angle(v1: "Vector3", v2: "Vector3") -> Number:
        raise NotImplementedError("angle method not yet implemented")
