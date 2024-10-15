import random
from copy import deepcopy

import numpy as np


class Azimuth:

    def __init__(self, mse):
        self.true_azimuth = self._generate_true_azimuth()
        self.mse = mse
        self.measured_azimuth = self._get_measured_azimuth()

    def _generate_true_azimuth(self):
        degree = random.randint(5, 355)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        return degree + minutes / 60 + seconds / 3600

    def _get_measured_azimuth(self):
        error = np.random.normal(loc=0, scale=self.mse)
        return self.true_azimuth + error / 3600

    def get_double_measurement(self, mse=None):
        double_azimuth = deepcopy(self)
        if mse is not None:
            double_azimuth.mse = mse
        double_azimuth.measured_azimuth = double_azimuth._get_measured_azimuth()
        return double_azimuth

    @staticmethod
    def get_str_for_measurement(measurement):
        degree = int(measurement)
        minutes = int((measurement - degree) * 60)
        seconds = round((measurement - degree - minutes / 60) * 3600)
        if seconds == 60:
            minutes += 1
            seconds = 0
        return f"{degree:3}°{minutes:02}\'{seconds:02}\""

    def __str__(self):
        return (f"Azimuth ({self.get_str_for_measurement(self.measured_azimuth)}, "
                f"mse = {self.mse:.1f})")

    def __repr__(self):
        return self.__str__()

if __name__ == "__main__":
    for _ in range(20):
        azimuth = Azimuth(30)
        d_azimuth = azimuth.get_double_measurement()
        print(azimuth.get_str_for_measurement(azimuth.measured_azimuth),
              d_azimuth.get_str_for_measurement(d_azimuth.measured_azimuth))