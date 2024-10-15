from Azimuth import Azimuth
from CONFIG import GYRO_MSE, ANGLE_MSE
from VariantGenerator import VariantGenerator


class Solver:

    def __init__(self, variant_generator: VariantGenerator, mse_poly_0=ANGLE_MSE, mse_gyro_0=GYRO_MSE):
        self.variant_generator = variant_generator
        self.df = variant_generator.get_measure_df(to_str=False)
        self.df_1 = None
        self.df_2 = None
        self.mse_poly_0 = mse_poly_0
        self.mse_gyro_0 = mse_gyro_0
        self.gyro_mse = None


    def solve_variant(self):
        self.solve_the_first_part()
        # self.solve_the_second_part()

    def solve_the_first_part(self):
        self.df_1 = self.df.copy(deep=True)
        self.df_1 = self.df_1.drop(["Poly_Azimuth", "num_of_angles"], axis=1)
        self.df_1["d"] = self.df_1["Gyro_2"] - self.df_1["Gyro_1"]
        self.df_1["dd"] = self.df_1["d"] ** 2
        self.df_1["|d|"] = abs(self.df_1["d"])
        if abs(self.df_1["d"].sum()) <= 0.25 * self.df_1["|d|"].sum():
            sum_of_dd = self.df_1["dd"].sum()
            gyro_mse = (sum_of_dd / (2 * len(self.df_1))) ** 0.5
            gyro_mse = Azimuth.get_str_for_measurement(gyro_mse)
        else:
            self.df_1["d\'"] = self.df_1["d"] - self.df_1["d"].sum() / len(self.df_1)
            self.df_1["d\'d\'"] = self.df_1["d\'"] ** 2
            sum_of_dd = self.df_1["d\'d\'"].sum()
            gyro_mse = (sum_of_dd / (2 * (len(self.df_1) - 1))) ** 0.5
            gyro_mse = Azimuth.get_str_for_measurement(gyro_mse)
        self.gyro_mse = gyro_mse


        print(f"{round(abs(self.df_1["d"].sum()) * 3600, 3)} <= {round(0.25 * self.df_1["|d|"].sum() * 3600, 3)}")

        sum_of_dd = self.df_1["dd"].sum()
        gyro_mse = (sum_of_dd / (2 * len(self.df_1))) ** 0.5
        gyro_mse = Azimuth.get_str_for_measurement(gyro_mse)
        self.gyro_mse = gyro_mse
        print(gyro_mse)
        print(self.df_1)

    def solve_the_second_part(self):
        self.df_2 = self.df.copy(deep=True)
        self.df_2["Gyro_AVR"] = (self.df_2["Gyro_2"] + self.df_2["Gyro_1"]) / 2
        self.df_2 = self.df_2.drop(["Gyro_1", "Gyro_2"], axis=1)
        self.df_2 = self.df_2[["Gyro_AVR", "Poly_Azimuth", "num_of_angles"]]
        self.df_2["p_gyro"] = 1
        self.df_2["p_poly"] = (self.gyro_mse ** 2)
        print(self.df_2)




if __name__ == "__main__":
    name = "Выстрчил Михаил Георгиевич"

    vg = VariantGenerator(name)
    solver = Solver(vg)
    solver.solve_variant()