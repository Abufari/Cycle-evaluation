import numpy as np
from scipy.integrate import simps
from scipy.interpolate import UnivariateSpline


class Cycle:
    """
    Class for defining one Cycle inside a UNAT-Measurement.

    """
    def __init__(self, x, y):
        # Fields
        self.cycle_maximums = []
        self.nullpoints = []
        self.envelope_coord_yx = []
        self.number_of_cycles = 0
        self.x_grid = []

        self.x = x
        self.y = y

    def analyse_cycle(self):
        """
        Decide if Cycle is evaluable in terms of energy contributions.
        Calibration files for example are not.
        """
        self.indices_of_nullpoints()
        self.indices_of_max_indents()
        self.get_number_of_cycles()
        self._get_maximum_forces()
        return self.is_valid_cycle()

    def indices_of_nullpoints(self) -> list:
        """
        Returns nullpoints of each Cycle as index of array
        """
        i, j = 0, 0
        nullpoints = []
        while i < len(self.x):
            if self.y[i] < 5:
                # now function is near zero
                j = i + 5
                try:
                    # move j forward until function goes up again
                    while self.y[j] < 5:
                        j += 1
                    min_cycle = np.argmin(self.x[i: j])  # go to most left point
                    nullpoints.append(i + min_cycle)
                    i = j + 5  # y[j] is already > 0, so j + 5 is for sure
                except IndexError:
                    pass
            i += 1
        self.nullpoints = nullpoints
        return nullpoints

    def indices_of_max_indents(self) -> list:
        """
        Returns all maximum values of each Cycle
        """
        nullpoints = self.nullpoints
        cycle_maximums = []
        i, j = 0, 1
        while j < len(nullpoints):
            # get most right point between to nullpoints
            # (not highest point, but farest right)
            cycle_maximum = np.argmax(self.x[nullpoints[i]: nullpoints[j]])
            cycle_maximums.append(nullpoints[i] + cycle_maximum)
            i += 1
            j += 1

        self.cycle_maximums = cycle_maximums
        return cycle_maximums

    def get_number_of_cycles(self) -> int:
        maximums = self.cycle_maximums
        self.number_of_cycles = len(maximums)
        return len(maximums)

    def is_valid_cycle(self) -> bool:
        """
        Make sure that not a single calibration cycle gets evaluated
        """
        if self.get_number_of_cycles() > 3:
            return True
        return False

    def _get_cycle_points(self, idx):
        """
        Gather all array indices of one single cycle

            idx: Number of cycle
        """
        maximums = self.cycle_maximums
        nullpoints = self.nullpoints
        # maximum_reload is not equal to maximum of next cycle!
        # You have to take the same x value of the maximum of your previous
        # cycle. Most likely these are not the exact same x values,
        # but thats what the univariate spline in evaluate_cycle is for
        maximum_reload = nullpoints[idx + 1]
        while self.x[maximum_reload] < self.x[maximums[idx]]:
            maximum_reload += 1  # when not true anymore, we've passed the value
        return (nullpoints[idx], maximums[idx], nullpoints[idx + 1],
                maximum_reload)

    def _get_maximum_forces(self):
        self.envelope_coord_yx.clear()
        for idx in range(self.get_number_of_cycles()):
            min1, max_indent, min2, max_indent2 = self._get_cycle_points(idx)
            try:
                # y_max is a few points left of x_max
                y_max = np.argmax(
                    self.y[max(max_indent - 10, 0): max_indent]
                                  ) + max_indent - 10
            except ValueError:
                # debug
                print('max_indent', max_indent)
            self.envelope_coord_yx.append((self.y[y_max], self.x[y_max]))
            self.x_grid.append(self.x[y_max])

    def evaluate_cycle(self, idx):
        """
        Get energy contributions of Cycle
            idx: Number of Cycle
        """
        # values of enveloping curve
        y_envelope = [i[0] for i in self.envelope_coord_yx[0:idx + 1]]
        x_envelope = [i[1] for i in self.envelope_coord_yx[0:idx + 1]]

        min1, max_indent, min2, max_indent2 = self._get_cycle_points(idx)

        # simple integrations
        loading = simps(self.y[min1:max_indent + 1],
                        self.x[min1:max_indent + 1])
        unloading = simps(self.y[max_indent:min2 + 1],
                          self.x[max_indent:min2 + 1])

        # build a spline, because you have to integrate the reloading curve
        # to the exact same x-value as the loading curve
        s = UnivariateSpline(self.x[min2:max_indent2 + 1],
                             self.y[min2:max_indent2 + 1])
        # go from min2 to max_indent, not max_indent2!
        xs = np.linspace(self.x[min2], self.x[max_indent], 100)
        ys = s(xs)
        reloading = simps(ys, xs)

        total = simps(y_envelope, x_envelope)

        elastic = - unloading
        plastic = loading - reloading
        friction = reloading + unloading
        plastic_total = total - reloading

        return elastic, plastic, friction, plastic_total
