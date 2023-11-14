from typing import Tuple, Literal


class CoplanarTrajectory:

    @staticmethod
    def generate(axis: Literal["x", "y"], start_xy_mm: Tuple[int, int], distance_mm: int = 10, repetitions: int = 2, go_to_start: bool = True, return_to_start: bool = True, auto_home=True):
        """
        Generates a simple coplanar trajectory in X or Y direction.

        :param axis: coplanar axis (X or Y)
        :param start_xy_mm: trajectory start point
        :param distance_mm: travel distance
        :param repetitions:
        :param go_to_start: go to start position first before repetitions
        :param return_to_start: return to X,Y start after all repetitions
        :param auto_home:
        :return: list of G-Code commands
        """

        ax = axis.upper()
        start_x_mm, start_y_mm = start_xy_mm
        start_axis_mm = start_x_mm if ax == "X" else start_y_mm

        commands = []

        if auto_home:
            commands.append("G28 O X Y Z")

        if go_to_start:
            commands.append(f"G1 X{start_x_mm} Y{start_y_mm}")

        for r in range(0, repetitions):
            commands.append(f"G1 {ax}{start_axis_mm}")
            commands.append(f"G1 {ax}{start_axis_mm + distance_mm}")
        if return_to_start:
            commands.append(f"G1 {ax}{start_axis_mm}")
        return commands
