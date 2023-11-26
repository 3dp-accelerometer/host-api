from typing import Tuple, Literal, List


class CoplanarTrajectory:

    @staticmethod
    def generate(axis: Literal["x", "y", "z"],
                 start_xyz_mm: Tuple[int, int, int],
                 distance_mm: int = 10,
                 step_repeat_count: int = 2,
                 go_to_start: bool = True,
                 return_to_start: bool = True,
                 auto_home=True) -> List[str]:
        """
        Generates a simple coplanar trajectory (step) in X, Y or Z direction.

        G-Code moves the tool to the start position from where it starts the forth and back movement.
        This is done in the specified axis direction.
        Specify negative distance to move in the opposite direction.

        :param axis: coplanar axis (X, Y or Z)
        :param start_xyz_mm: trajectory start point
        :param distance_mm: travel distance
        :param step_repeat_count: how often to repeat a step
        :param go_to_start: go to start position first before repetitions
        :param return_to_start: return to X,Y start after all repetitions
        :param auto_home:
        :return: list of G-Code commands
        """

        start_x_mm, start_y_mm, start_z_mm = start_xyz_mm
        ax = axis.upper()
        start_axis_mm = {"X": start_x_mm, "Y": start_y_mm, "Z": start_z_mm}[ax]

        commands: List[str] = []

        if auto_home:
            commands.append("G28 O X Y Z")

        if go_to_start:
            commands.append(f"G1 X{start_x_mm} Y{start_y_mm} Z{start_z_mm}")

        for _step in range(0, step_repeat_count):
            commands.append(f"G1 {ax}{start_axis_mm}")
            commands.append(f"G1 {ax}{start_axis_mm + distance_mm}")

        if return_to_start:
            commands.append(f"G1 {ax}{start_axis_mm}")

        return commands
